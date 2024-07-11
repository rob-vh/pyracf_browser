import pandas as pd

def join_connect_groups_for_user(r,index):
    return list(index)+list([g for g in r.connects.loc[(slice(None),index),].droplevel(1).index])
    
def join_dataset_permits_for_id(r,index):
    try:
        r1 = r.datasetAccess.find(None,index)
    except KeyError:
        r1 = r.datasetAccess.head(0)
    try:
        r2 = r.datasetConditionalAccess.find(None,index)
    except (KeyError,TypeError):
        r2 = r.datasetConditionalAccess.head(0)
    return pd.concat([r1.stripPrefix(),r2.stripPrefix()])

def join_general_permits_for_id(r,index):
    try:
        r1 = r.generalAccess.find(None,None,index)
    except KeyError:
        r1 = r.generalAccess.head(0)
    try:
        r2 = r.generalConditionalAccess.find(None,None,index)
    except (KeyError,TypeError):
        r2 = r.generalConditionalAccess.head(0)
    return pd.concat([r1.stripPrefix(),r2.stripPrefix()])

def try_dataset_permits(r,index):
    try:
        r1 = r.datasetAccess.loc[index]
    except KeyError:
        r1 = r.datasetAccess.head(0)
    try:
        r2 = r.datasetConditionalAccess.loc[index]
    except (KeyError,TypeError):
        r2 = r.datasetConditionalAccess.head(0)
    return pd.concat([r1.stripPrefix(),r2.stripPrefix()])

def try_general_permits(r,index):
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
    'connects': lambda r,index: r.connectData.loc[index],
    'permits on data sets': lambda r,index: join_dataset_permits_for_id(r,index),
    'permits on general resources': lambda r,index: join_general_permits_for_id(r,index),
    },
'user':  {
    'connects': lambda r,index: r.connectData.loc[(slice(None),index),],
    'permits on data sets': lambda r,index: join_dataset_permits_for_id(r,index),
    'permits on general resources': lambda r,index: join_general_permits_for_id(r,index),
    'data sets in scope': lambda r,index: join_dataset_permits_for_id(r,join_connect_groups_for_user(r,index)).acl(resolve=True).find(user=index),
    'general resources in scope': lambda r,index: join_general_permits_for_id(r,join_connect_groups_for_user(r,index)).acl(resolve=True).find(user=index),
    },
'dataset': {
    'permits':     try_dataset_permits,
    'acl':         lambda r,index: r.datasets.loc[index].acl(),
    'acl explode': lambda r,index: r.datasets.loc[index].acl(explode=True),
    'acl resolve': lambda r,index: r.datasets.loc[index].acl(resolve=True)
    },
'general resource': {
    'permits':     try_general_permits,
    'acl':         lambda r,index: r.generals.loc[index].acl(),
    'acl explode': lambda r,index: r.generals.loc[index].acl(explode=True),
    'acl resolve': lambda r,index: r.generals.loc[index].acl(resolve=True),
    }
}

entity_action_names = {e:[''] for e in entity_actions.keys()}
_ = [entity_action_names[e].extend([a for a in entity_actions[e].keys()]) for e in entity_actions.keys()]

def action_driver(r,entity,index,action):
    '''multi page action module
    
    args:
        r: RACF object
        entity: type of object selected
        index: list of object selectors: index values
        action: action name

    returns:
        data frame
    '''
    df = entity_actions[entity][action](r,index)
    if isinstance(df,pd.DataFrame) and hasattr(df,'_fieldPrefix'):
        columns = [c for c in df.columns if c.find('RECORD_TYPE')==-1]
        df = df.reset_index(drop=True)[columns]
    return df
    
