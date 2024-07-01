import streamlit as st
from make_stylable import make_stylable
import time

def MaybeUpper(text):
    return text if mixedcase else text.upper()

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

@st.cache_data
def get_segments():
    return segment_getter(r)
segments = get_segments()

select_frame = st.sidebar
header = st.container()
output_frame = st.container()
input_table = ''
final_processing = []

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
        # create a tab for each segment available, or 1 tab for the base segment
        snames = list(segments[select_entity].keys()) if select_entity in segments else ['base']
        (stabs) = st.tabs(snames)
        # st.tabs does not have a "name" or "id" attribute, so we loop over the names...
        for sindex in range(len(snames)):
            segment = snames[sindex]
            track('start segment tab',segment)
            with stabs[sindex]:
                if len(snames)==1:
                    hide_segment = False
                else:
                    # initially show only base segment (sindex==0)
                    if select_entity+'_hide_'+segment not in st.session_state: st.session_state[select_entity+'_hide_'+segment] = (sindex!=0)
                    hide_segment = st.toggle('hide',key=select_entity+'_hide_'+segment)

                if sindex==0:  # base segment, field names without prefix
                    rubbish = ['RECORD_TYPE','NAME','CLASS_NAME','CLASS','ALTER_CNT','CONTROL_CNT','UPDATE_CNT','READ_CNT','LASTREF_DATE']
                    if select_entity in entity_data_selector:  # preferred fields listed
                        columns = entity_data_selector[select_entity]
                    else:  # system profiles show all fields
                        columns = [c for c in r.table(input_table).columns if c.split('_',1)[1] not in rubbish]
                else:  # keep the prefix
                    input_table = segments[select_entity][segment]
                    rubbish = ['RECORD_TYPE','NAME','CLASS_NAME','CLASS']
                    columns = [c for c in r.table(input_table).columns if c.split('_',1)[1] not in rubbish]
                hide_columns = [c for c in r.table(input_table).columns if c.split('_',1)[0]==input_table and c.split('_',1)[1] in rubbish]
                select_datafields = {}
                skip_datafields = {}

                track('start with columns')
                for c in columns:
                    if c[0:15]=='USOPR_ROUTECODE':continue  # 128 fields!
                    with make_stylable(st.container(),
                        css_key="compound_header",
                        css_styles="""
                           div.stTextInput {
                              margin-top: -0.4em
                           }
                           div.stCheckbox {
                                min-height: 0;
                                padding-right: 0;
                                margin-block: -0.8em;
                           }
                        """
                    ):
                        c1,c2 = st.columns([5,4],vertical_alignment="center")
                        c1.write(c.replace(input_table+'_',''))
                        #  testing values from session_states is expensive, and default value is false anyway
                        # if select_entity+'_hide_'+c not in st.session_state: st.session_state[select_entity+'_hide_'+c] = False
                        # if select_entity+'_skip_'+c not in st.session_state: st.session_state[select_entity+'_skip_'+c] = False
                        chide = c2.toggle('hide',key=select_entity+'_hide_'+c)
                        cskip = c2.toggle('skip',key=select_entity+'_skip_'+c)
                        cval = st.text_input(c, key=select_entity+'_value_'+c,
                                           help='Enter pattern, \*\* for all non-empty values, \*text\* to search anywhere, or YES/NO for flag fields',
                                           label_visibility="collapsed")
                    if cval:
                        if cskip:
                            skip_datafields.update({c:MaybeUpper(cval)})
                        else:
                            select_datafields.update({c:MaybeUpper(cval)})
                    if chide:
                        hide_columns.append(c)
                if sindex==0 and select_entity in entity_data_selector:  # base segments, for all but the system profiles
                    c = 'irrelevant fields'
                    c1,c2 = st.columns([5,4],vertical_alignment="center")
                    c1.write(c)
                    if select_entity+'_hide_'+c not in st.session_state: st.session_state[select_entity+'_hide_'+c] = True
                    chide = c2.toggle('hide',key=select_entity+'_hide_'+c)
                    if chide:
                        hide_columns.extend([c for c in r.table(input_table).columns if c not in columns])

            final_processing.append({'table': input_table,
                                     'segment': segment,
                                     'hide': hide_segment,
                                     'hide_columns': hide_columns,
                                     'select_keys': select_keys,
                                     'select_datafields': select_datafields,
                                     'skip_datafields': skip_datafields})
            track('end segment tab',segment)

input_table = ''
for p in final_processing:
    if not p['hide'] or p['select_datafields'] or p['skip_datafields']:
        needed_columns = list(p['select_datafields'].keys())+list(p['skip_datafields'].keys())
        if p['hide']:  # hide whole segment, but we need to do select/skip
            columns = needed_columns
        elif p['hide_columns']:
            columns = [c for c in r.table(p['table']).columns if c in needed_columns or c not in p['hide_columns']]
        else:
            columns = slice(None)
        if input_table=='':  # first useful table
            input_table = p['table']
            df = r.table(p['table'])[columns]
        else:
            df = df.join(r.table(p['table'])[columns])
        df = df.find(*p['select_keys'],**p['select_datafields']).skip(**p['skip_datafields'])
        if p['select_datafields'] or p['skip_datafields']:
            if p['hide']:  # hide whole segment
                drop_columns = r.table(p['table']).columns
            elif p['hide_columns']:
                drop_columns = p['hide_columns']
            columns = [c for c in df.columns if c not in drop_columns]
            df = df[columns]
        if p['segment']=='base':
            df = df.stripPrefix()

track('frame ready')

with header:
    sum_select_datafields = {}
    sum_skip_datafields = {}
    for p in final_processing:
        sum_select_datafields.update(p['select_datafields'])
        sum_skip_datafields.update(p['skip_datafields'])

    st.header(f"pyracf: {select_entity}s")
    if input_table:
        st.text(f'{df.shape[0]} records: {select_keys} {sum_select_datafields} not{sum_skip_datafields}')

with output_frame:
    if input_table:
        st.dataframe(df)

