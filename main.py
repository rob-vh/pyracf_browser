import streamlit as st

@st.cache_data
def get_RACF(*args,**kwds):
    import sys, time
    new_path = r'/home/rob/Documents/henri/pyracf-dev-0.9/src/'
    sys.path.append(new_path)
    
    from pyracf import RACF
    r = RACF(*args,**kwds)
    r.parse()
    while r._state != RACF.STATE_READY:
        time.sleep(0.5)
    return r
r = get_RACF('/home/rob/Documents/henri/synthetic.unload')

from field_spec import entity_key_selector, entity_data_selector, system_profile_getter

select_frame = st.sidebar 
header = st.container()
output_frame = st.container()
input_table = ''
select_keys = []
select_datafields = {}

def MaybeUpper(text):
    return text if mixedcase else text.upper()

with select_frame:
    mixedcase = st.toggle('Mixed case criteria',False)
    select_entity = st.radio('Select entity type',
                    entity_key_selector.keys())
    if select_entity:
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
                    fieldname = st.radio('How to select',fields)
                if fieldname.find('match')!=-1:
                    select_datafields['match']=MaybeUpper(st.text_input(fieldname,help='Enter fully qualified name without quotes'))
                else:
                    pattern = st.text_input(fieldname,help='Enter generic pattern, or leave empty to select all profiles')
                    if pattern:
                        select_keys.append(MaybeUpper(pattern))
                    else:
                        select_keys.append(None)
            i += 1
        
        rubbish = ['RECORD_TYPE','NAME','CLASS_NAME','CLASS','ALTER_CNT','CONTROL_CNT','UPDATE_CNT','READ_CNT','LASTREF_DATE']
        if select_entity in entity_data_selector:
            columns = entity_data_selector[select_entity]
            output_columns = columns+[c for c in r.table(input_table).stripPrefix().columns if c not in rubbish and c not in columns]
        else:
            columns = [c for c in r.table(input_table).stripPrefix().columns if c not in rubbish]
            output_columns = columns
        with st.container():
            for c in columns:
                cv = st.text_input(c, help='Enter pattern, \*\* for all non-empty values, \*text\* to search anywhere, or YES/NO for flag fields')
                if cv:
                    select_datafields.update({c:MaybeUpper(cv)})

with header:
    st.header(f"pyracf: {select_entity}s")
    st.text(str(select_keys)+str(select_datafields))
    
with output_frame:
    if input_table not in ('','*'):
        st.dataframe(r.table(input_table).find(*select_keys,**select_datafields).stripPrefix()[output_columns])

    
