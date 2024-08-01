import pandas as pd
from utils import connectAttributes

def join_connect_groups_for_users(r,index):
    return list(index)+list([g for g in r.connects.loc[(slice(None),index),].droplevel(1).index])

def join_dataset_permits_for_id(r,index):
    r1 = r.datasetAccess.find(None,index)
    r2 = r.datasetConditionalAccess.find(None,index)
    return pd.concat([r1.stripPrefix(),r2.stripPrefix()])

def join_general_permits_for_id(r,index):
    r1 = r.generalAccess.find(None,None,index)
    r2 = r.generalConditionalAccess.find(None,None,index)
    return pd.concat([r1.stripPrefix(),r2.stripPrefix()])

def join_dataset_permits(r,index):
    r1 = r.datasetAccess.find(index)
    r2 = r.datasetConditionalAccess.find(index)
    return pd.concat([r1.stripPrefix(),r2.stripPrefix()])

def join_general_permits(r,index):
    '''select general resource profiles, using an index with 2 columns, so find() doesn't work'''
    try:
        r1 = r.generalAccess.droplevel([2,3]).loc[index]
    except KeyError:
        r1 = r.generalAccess.head(0)
    try:
        r2 = r.generalConditionalAccess.droplevel([2,3]).loc[index]
    except (KeyError,TypeError):
        r2 = r.generalConditionalAccess.head(0)
    return pd.concat([r1.stripPrefix(),r2.stripPrefix()])

entity_actions = {
'group': {
    'details': lambda r,index: r.groups.find(index).stripPrefix().T,
    'connects': lambda r,index: r.connectData.find(index).stripPrefix().pipe(connectAttributes),
    'connect matrix': lambda r,index: r.connectData.find(index).stripPrefix().pipe(connectAttributes).pivot(index='GRP_ID',columns='NAME',values='attribs').fillna(''),
    'connect matrix T': lambda r,index: r.connectData.find(index).stripPrefix().pipe(connectAttributes).pivot(index='NAME',columns='GRP_ID',values='attribs').fillna(''),
    'permits on data sets': lambda r,index: join_dataset_permits_for_id(r,index),
    'permits on general resources': lambda r,index: join_general_permits_for_id(r,index),
    },
'user':  {
    'details': lambda r,index: r.users.find(index).stripPrefix().T,
    'connects': lambda r,index: r.connectData.loc[(slice(None),index),].stripPrefix().pipe(connectAttributes),
    'connect matrix': lambda r,index: r.connectData.loc[(slice(None),index),].stripPrefix().pipe(connectAttributes).pivot(index='NAME',columns='GRP_ID',values='attribs').fillna(''),
    'connect matrix T': lambda r,index: r.connectData.loc[(slice(None),index),].stripPrefix().pipe(connectAttributes).pivot(index='GRP_ID',columns='NAME',values='attribs').fillna(''),
    'permits on data sets': lambda r,index: join_dataset_permits_for_id(r,index),
    'permits on general resources': lambda r,index: join_general_permits_for_id(r,index),
    'data sets in scope': lambda r,index: join_dataset_permits_for_id(r,join_connect_groups_for_users(r,index)).acl(resolve=True).find(user=index),
    'general resources in scope': lambda r,index: join_general_permits_for_id(r,join_connect_groups_for_users(r,index)).acl(resolve=True).find(user=index),
    },
'connect': {
    'details': lambda r,index: r.connectData.loc[index].stripPrefix().T,
    },
'dataset': {
    'details': lambda r,index: r.datasets.find(index).stripPrefix().T,
    'permits':     join_dataset_permits,
    'access matrix': lambda r,index: r.datasets.loc[index].acl().pivot(index='NAME',columns='AUTH_ID',values='ACCESS').fillna(''),
    'acl':         lambda r,index: r.datasets.loc[index].acl(),
    'acl explode': lambda r,index: r.datasets.loc[index].acl(explode=True),
    'acl resolve': lambda r,index: r.datasets.loc[index].acl(resolve=True)
    },
'general resource': {
    'details': lambda r,index: r.generals.loc[index].stripPrefix().T,
    'permits':     join_general_permits,
    'access matrix': lambda r,index: r.generals.loc[index].acl().pivot(index=['CLASS_NAME','NAME'],columns='AUTH_ID',values='ACCESS').fillna(''),
    'acl':         lambda r,index: r.generals.loc[index].acl(),
    'acl explode': lambda r,index: r.generals.loc[index].acl(explode=True),
    'acl resolve': lambda r,index: r.generals.loc[index].acl(resolve=True),
    },
'system profile': {
        'details': lambda table,index: table.loc[index].stripPrefix().T,
    }
}

entity_action_names = {e:[''] for e in entity_actions.keys()}
_ = [entity_action_names[e].extend([a for a in entity_actions[e].keys()]) for e in entity_actions.keys()]

def action_driver(r,entity,index,action,table=None):
    '''multi page action module

    args:
        r: RACF object
        entity: type of object selected
        index: list of object selectors: index values
        action: action name

    returns:
        data frame
    '''
    # print(entity,action,index)
    if action in entity_actions[entity]:
        if table is None: # action picks the right table(s)
            df = entity_actions[entity][action](r,index)
        else: # system table selected by main app
            df = entity_actions[entity][action](table,index)
        if isinstance(df,pd.DataFrame) and hasattr(df,'_fieldPrefix'):
            if 'RECORD_TYPE' in df.columns:
                columns = [c for c in df.columns if c.find('RECORD_TYPE')==-1]
                df = df.reset_index(drop=True)[columns]
            elif 'RECORD_TYPE' in df.index:
                df = df.drop('RECORD_TYPE')
        return df

