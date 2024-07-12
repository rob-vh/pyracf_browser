import streamlit as st
from make_stylable import make_stylable
import time
import pandas as pd

def MaybeUpper(text):
    '''relies on global (result of a switch) var mixedcase to apply upper() to selection values'''
    return text if mixedcase else text.upper()

def dictField(d,f,default=None):
    '''conditionally return a dict member value'''
    return d[f] if f in d else default

@st.cache_data
def get_config():
    import toml
    with open('main.toml', 'r') as f:
        c = toml.load(f)
    if 'track' not in c:
        c['track'] = {}
    if 'time' not in c['track']:
        c['track']['time'] = False
    else:
        c['track']['time'] = time.time()
    return c
config = get_config()

def track(*stage):
    if config['track']['time']:
        t = time.time()
        print(f"{t-config['track']['time']:.6f}",*stage)
        config['track']['time'] = t
    return
track('tracker installed')

@st.cache_resource
def get_RACF(*args,**kwds):
    import sys, time
    if config['pyracf_path'] and config['pyracf_path'] not in sys.path:
        sys.path.insert(1,config['pyracf_path'])

    from pyracf import RACF
    r = RACF(*args,**kwds)
    r.parse()
    while r._state != RACF.STATE_READY:
        time.sleep(0.5)
    return r
r = get_RACF(config['unload'])

from field_spec import entity_key_selector, entity_data_selector, segment_getter, system_profile_getter
from action_spec import entity_action_names, action_driver

@st.cache_data
def get_segment_defs():
    # create {entity : {segment: { 'table': table } } }
    segment_defs = {'connect': {'base': {} }, 'system profile': {'base': {} } }
    segment_names = segment_getter(r)  # {entity: {segment: table} }
    for e in entity_data_selector.keys():
        if e in segment_names:
            segment_defs[e] = {s:{'table': segment_names[e][s]} for s in segment_names[e].keys()}
        else:
            segment_defs[e] = {'base': {} }
    return segment_defs

if 'query_state' in st.session_state:
    query_state = st.session_state['query_state']
else:
    query_state = get_segment_defs()

select_frame = st.sidebar
header = st.container()
output_frame = st.container()
input_table = ''

with select_frame:
    track('top of loop')
    # st.session_state gets lost after evaluation of another entity type, so we make it persistent by pushing each variable in
    # see https://discuss.streamlit.io/t/session-state-resets-when-i-press-a-button/50516/4
    for s in st.session_state.keys():
        st.session_state[s] = st.session_state[s]

    mixedcase = st.toggle('Mixed case criteria',False)
    select_entity = st.radio('Select entity type',
                    entity_key_selector.keys())
    if select_entity:
        select_keys = []
        i = -1
        for fields in entity_key_selector[select_entity]:
            if i==-1:
                input_table = fields
                if fields == '*':  # system profiles
                    input_tables = {k:t for k,t in system_profile_getter(r).items() if hasattr(r.table(t),'empty') and not r.table(t).empty}
                    input_table = input_tables[st.radio('Select table',input_tables.keys())]
                    select_keys.append(None)
            else:
                if type(fields) == str:
                    fieldname = fields
                elif type(fields) == list:
                    fieldname = st.radio('How to select',fields,key=select_entity+'_pattern_or_match_'+str(i))
                if fieldname.find('match')!=-1:
                    select_datafields['match']=MaybeUpper(st.text_input(fieldname,key=select_entity+'_match_value_'+str(i),help='Enter fully qualified name without quotes'))
                else:
                    pattern = st.text_input(fieldname,key=select_entity+'_pattern_value_'+str(i),help='Enter generic pattern, or leave empty to select all profiles')
                    if pattern:
                        select_keys.append(MaybeUpper(pattern))
                    else:
                        select_keys.append(None)
            i += 1
        track('keys done')

        # create a button for each segment available, or 1 tab for the base segment
        query_segments = query_state[select_entity]
        if len(query_segments.keys())==1:
            segment = 'base'
        else:
            cs = make_stylable(st.container(),
                css_key='segment-buttons',
                css_styles="""
                {
                    display: flex;
                    flex-direction: row;
                    flex-wrap: wrap;
                    & div {
                        display: flex;
                        flex-direction: row;
                        flex-wrap: wrap;
                        width: auto;
                        & ~ div {
                            width: auto;
                        }
                    }
                    & div.stButton {
                        width: auto ! important;
                    }
                    & div.stTooltipIcon > div:last-child {
                        display: none;
                    }
                }
                """)

            with cs:
                for segment in query_segments.keys():
                    color = ''
                    hide = (1-dictField(st.session_state,select_entity+'_show_'+segment,segment!='base'))
                    ix = 2*hide + (dictField(query_segments[segment],'filters',0)==0)
                    colors = ['green','blue','red','grey']
                    helps = ['segment with selection criteria','segment data on output','hidden segment with selection criteria','no segment data on output']
                    query_segments[segment]['open'] = st.button(f":{colors[ix]}[{segment}]", help=helps[ix])

            segment_clicked = [s for s in query_segments.keys() if query_segments[s]['open']]
            if len(segment_clicked)==1:
                segment = segment_clicked[0]
            elif select_entity+'_segment' in st.session_state:
                segment = st.session_state[select_entity+'_segment']
            else:
                segment = 'base'
            st.session_state[select_entity+'_segment'] = segment

        track('start segment tab',segment)
        cs = make_stylable(st.container(),
            css_key='field-prompts',
            css_styles="""
            {
               & div.stTextInput {
                  margin-top: -0.4em;
               }
               & div.stCheckbox {
                    min-height: 0;
                    padding-right: 0;
                    margin-block: -0.4em;
                    margin-right: -1em;
               }
            }
            """)
        with cs:
            if segment=='base':  # base segment, field names without prefix
                rubbish = ['RECORD_TYPE','NAME','CLASS_NAME','CLASS','ALTER_CNT','CONTROL_CNT','UPDATE_CNT','READ_CNT','LASTREF_DATE']
                if select_entity in entity_data_selector:  # preferred fields listed
                    columns = entity_data_selector[select_entity]
                else:  # system profiles show all fields
                    columns = [c for c in r.table(input_table).columns if c.split('_',1)[1] not in rubbish]
            else:  # keep the prefix
                input_table = query_state[select_entity][segment]['table']
                rubbish = ['RECORD_TYPE','NAME','CLASS_NAME','CLASS']
                columns = [c for c in r.table(input_table).columns if c.split('_',1)[1] not in rubbish]
            hide_columns = [c for a,b,c in [c.split('_',1)+[c] for c in r.table(input_table).columns] if a==input_table and b in rubbish]
            select_datafields = {}
            skip_datafields = {}

            if len(query_segments)==1:
                show_segment = True
                c2 = st.container()
            else:
                c1,c2 = st.columns(2)
                if select_entity+'_show_'+segment not in st.session_state: st.session_state[select_entity+'_show_'+segment] = (segment=='base')
                show_segment = c1.toggle('show segment',key=select_entity+'_show_'+segment)

            def reset_columns(reset,columns):
                for c in columns:
                    st.session_state[select_entity+'_show_'+c] = reset
            if select_entity+'_show_all_cols_'+segment not in st.session_state: st.session_state[select_entity+'_show_all_cols_'+segment] = True
            show_all_cols = c2.toggle('show all cols',key=select_entity+'_show_all_cols_'+segment,
                on_change=reset_columns,args=(not st.session_state[select_entity+'_show_all_cols_'+segment],columns))

            track('start with columns')
            for c in columns:
                c1,c2 = st.columns([5,2],vertical_alignment="center")
                cval = c1.text_input(c.replace(input_table+'_',''), key=select_entity+'_value_'+c,
                                   help='Enter pattern, \*\* for all non-empty values, \*text\* to search anywhere, or YES/NO for flag fields')
                if select_entity+'_show_'+c not in st.session_state: st.session_state[select_entity+'_show_'+c] = True
                if select_entity+'_skip_'+c not in st.session_state: st.session_state[select_entity+'_skip_'+c] = False
                cshow = c2.toggle('show',key=select_entity+'_show_'+c)
                cskip = c2.toggle('skip',key=select_entity+'_skip_'+c)
                if cval:
                    if cskip:
                        skip_datafields.update({c:MaybeUpper(cval)})
                    else:
                        select_datafields.update({c:MaybeUpper(cval)})
                if not cshow:
                    hide_columns.append(c)

            irrelevant_columns = []
            if segment=='base' and select_entity in entity_data_selector:  # base segments, for all but the system profiles
                c = 'irrelevant fields'
                c1,c2 = st.columns([5,4],vertical_alignment="center")
                c1.write(c)
                if select_entity+'_show'+c not in st.session_state: st.session_state[select_entity+'_show_'+c] = False
                cshow = c2.toggle('show',key=select_entity+'_show_'+c)
                if cshow:
                    irrelevant_columns = [c for c in r.table(input_table).columns if c not in columns]

        query_segments[segment].update({'table': input_table,
                                 'segment': segment,
                                 'show': show_segment,
                                 'columns': columns+irrelevant_columns,
                                 'hide_columns': hide_columns,
                                 'select_keys': select_keys,
                                 'select_datafields': select_datafields,
                                 'skip_datafields': skip_datafields,
                                 'filters': len(select_datafields)+len(skip_datafields)})

        st.session_state['query_state'] = query_state
        track('end segment tab',segment)

input_table = ''
for p in query_segments.values():
    if not 'columns' in p: continue
    if p['show'] or p['select_datafields'] or p['skip_datafields']:
        needed_columns = list(p['select_datafields'].keys())+list(p['skip_datafields'].keys())
        if not p['show']:  # hide whole segment, but we need to do select/skip
            columns = needed_columns
        elif p['hide_columns']:
            columns = [c for c in p['columns'] if c not in p['hide_columns']]
            columns.extend([c for c in needed_columns if c not in columns])
        else:
            columns = p['columns']
        if input_table=='':  # first useful table
            input_table = p['table']
            df = r.table(p['table'])[columns]
        else:
            df = df.join(r.table(p['table'])[columns])
        df = df.find(*p['select_keys'],**p['select_datafields']).skip(**p['skip_datafields'])
        if p['select_datafields'] or p['skip_datafields']:
            if not p['show']:  # hide whole segment
                drop_columns = r.table(p['table']).columns
            elif p['hide_columns']:
                drop_columns = p['hide_columns']
            columns = [c for c in df.columns if c not in drop_columns]
            df = df[columns]
        if p['segment']=='base':
            df = df.stripPrefix()

track('frame ready')

# dialog window for actions on selected profiles
@st.experimental_dialog('action results',width='large')
def action_frame(df,frame):
    selected_rows = df.iloc[frame['selection']['rows']].index
    print(selected_rows)
    if len(selected_rows)==1:
        profiles = selected_rows[0]
    elif selected_rows.ndim==1:
        profiles = ','.join(selected_rows)
    else:
        profiles = 'selected profiles'
    action = st.selectbox('Select action for '+profiles, entity_action_names[select_entity],key='action_select')
    if action:
        result = action_driver(r, select_entity, selected_rows, action)
        if isinstance(result,pd.DataFrame):
            st.dataframe(result, use_container_width=True, key='action_frame')

with header:
    st.header(f"pyracf: {select_entity}s")
    if input_table:
        sum_select_datafields = {}
        sum_skip_datafields = {}
        for p in query_segments.values():
            if 'select_datafields' in p:
                sum_select_datafields.update(p['select_datafields'])
            if 'skip_datafields' in p:
                sum_skip_datafields.update(p['skip_datafields'])
        st.text(f'{df.shape[0]} records: {select_keys} {sum_select_datafields} not{sum_skip_datafields}')

with output_frame:
    if input_table:
        frame = st.dataframe(df, on_select="rerun", selection_mode="multi-row", use_container_width=True)
        if select_entity in entity_action_names:
            go_action = st.button('Select one or more table rows and press button')
        if go_action and len(frame['selection']['rows'])>0:
            action_frame(df,frame)

