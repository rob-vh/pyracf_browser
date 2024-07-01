entity_key_selector = {
'group': ['GPBD','group name'],
'user': ['USBD','user ID'],
'connect': ['USCON','group name','user ID'],
'dataset': ['DSBD',['profile','dataset name match']],
'general resource': ['GRBD','class',['profile','resource match']],
'system profile': ['*','profile']
}
entity_data_selector = {
'group': '''GPBD_OWNER_ID GPBD_SUPGRP_ID GPBD_UNIVERSAL  GPBD_INSTALL_DATA
            GPBD_NOTERMUACC GPBD_UACC GPBD_MODEL GPBD_CREATE_DATE'''.split(),
'user': '''USBD_PROGRAMMER USBD_OWNER_ID USBD_DEFGRP_ID
           USBD_SPECIAL USBD_OPER USBD_AUDITOR USBD_ROAUDIT
           USBD_REVOKE USBD_REVOKE_DATE USBD_RESUME_DATE
           USBD_ATTRIBS USBD_UAUDIT
           USBD_MFA_FALLBACK USBD_REVOKE_CNT
           USBD_PWD_INTERVAL USBD_PWD_DATE USBD_PWD_GEN USBD_PWD_ASIS USBD_PWD_ALG
           USBD_PHR_INTERVAL USBD_PHR_DATE USBD_PHR_GEN USBD_PHR_ALG
           USBD_PWDENV_EXISTS USBD_PPHENV_EXISTS
           USBD_CREATE_DATE USBD_LASTJOB_TIME USBD_LASTJOB_DATE
           USBD_INSTALL_DATA
           USBD_ADSP USBD_GRPACC USBD_NOPWD USBD_OIDCARD
           USBD_MODEL
           USBD_SECLEVEL USBD_SECLABEL'''.split(),
'connect': ['USCON_GRP_SPECIAL', 'USCON_GRP_OPER', 'USCON_GRP_AUDIT', 'GPMEM_AUTH',
             'USCON_REVOKE', 'USCON_REVOKE_DATE', 'USCON_RESUME_DATE',
             'USCON_CONNECT_DATE', 'USCON_OWNER_ID', 'USCON_LASTCON_DATE', 'USCON_LASTCON_TIME', 'USCON_INIT_CNT',
             'USCON_NOTERMUACC','USCON_UACC', 'USCON_GRP_ADSP','USCON_GRP_ACC'],
'dataset': '''DSBD_UACC IDSTAR_ACCESS ALL_USER_ACCESS DSBD_WARNING DSBD_ERASE
              DSBD_GENERIC DSBD_VOL DSBD_OWNER_ID DSBD_NOTIFY_ID
              DSBD_AUDIT_LEVEL DSBD_AUDIT_OKQUAL DSBD_AUDIT_FAQUAL
              DSBD_GAUDIT_LEVEL DSBD_GAUDIT_OKQUAL DSBD_GAUDIT_FAQUAL
              DSBD_LEVEL DSBD_SECLEVEL DSBD_SECLABEL DSBD_INSTALL_DATA
              DSBD_CREATE_DATE DSBD_LASTCHG_DATE'''.split(),
'general resource': '''GRBD_UACC IDSTAR_ACCESS ALL_USER_ACCESS GRBD_WARNING
                       GRBD_GENERIC GRBD_OWNER_ID GRBD_NOTIFY_ID GRBD_APPL_DATA
                       GRBD_AUDIT_LEVEL GRBD_AUDIT_OKQUAL GRBD_AUDIT_FAQUAL
                       GRBD_GAUDIT_LEVEL GRBD_GAUDIT_OKQUAL GRBD_GAUDIT_FAQUAL
                       GRBD_LEVEL GRBD_SECLEVEL GRBD_SECLABEL GRBD_INSTALL_DATA
                       GRBD_CREATE_DATE GRBD_LASTCHG_DATE'''.split()
}

def segment_getter(r):
    entities = {
'group': {
        'base': {'table': 'GPBD', 'rest': ['GPSGRP']},
        'csdata': {'table': 'GPCSD'},
        'DFP': {'table': 'GPDFP'},
        'OMVS': {'table': 'GPOMVS'},
        'OVM': {'table': 'GPOVM'},
        'TME': {'table': 'GPTME'},
        'usrdata': {'table': 'GPINSTD'},
    },
'user': {
        'base': {'table': 'USBD', 'rest': ['USCAT','USCLA']},
        'csdata': {'table': 'USCSD'},
        'TSO': {'table': 'USTSO'},
        'CICS': {'table': 'USCICS', 'rest': ['USCOPC','USCRSL','USCTSL']},
        'DFP': {'table': 'USDFP'},
        'LANGUAGE': {'table': 'USLAN'},
        'OPERPARM': {'table': 'USOPR', 'rest': ['USOPRP']},
        'OMVS': {'table': 'USOMVS'},
        'WORKDATA': {'table': 'USWRK'},
        'MFA': {'table': 'USMFA'},
        'MPOL': {'table': 'USMPOL'},
        'MFAC': {'table': 'USMFAC'},
        'NETVIEW': {'table': 'USNETV', 'rest': ['USNOPC','USNDOM']},
        'RSSF': {'table': 'USRSF'},
        'DCE': {'table': 'USDCE'},
        'KERB': {'table': 'USKERB'},
        'LNOTES': {'table': 'USLNOT'},
        'NDS': {'table': 'USNDS'},
        'PROXY': {'table': 'USPROXY'},
        'EIM': {'table': 'USEIM'},
        'OVM': {'table': 'USOVM'},
        'CERT': {'table': 'USCERT'},
        'NMAP': {'table': 'USNMAP'},
        'DMAP': {'table': 'USDMAP'},
        'usrdata': {'table': 'USINSTD'},
    },
'dataset': {
        'base': {'table': 'DSBD', 'rest': ['DSCAT', 'DSVOL','DSACC','DSCACC','DSMEM']},
        'csdata': {'table': 'DSCSD'},
        'DFP': {'table': 'DSDFP'},
        'TME': {'table': 'DSTME'},
        'usrdata': {'table': 'DSINSTD'}
    },
'general resource': {
        'base': {'table': 'GRBD', 'rest': ['GRCAT','GRACC','GRCACC','GRMEM']},
        'csdata': {'table': 'GRCSD'},
        'TVOL': {'table': 'GRTVOL'},
        'VOL': {'table': 'GRVOL'},
        'usrdata': {'table': 'GRINSTD'},
    },
'tape': {
        'base': {'table': 'GRTVOL', 'rest': ['GRVOL']},
        'csdata': {'table': 'GRCSD'},
        'usrdata': {'table': 'GRINSTD'},
    }}
    result = {}
    for k1,e1 in entities.items():
        result[k1] = {}
        for k2,e2 in e1.items():
            if 'table' in e2:
                if  hasattr(r.table(e2['table']),'empty') and not r.table(e2['table']).empty:
                    result[k1].update({k2:e2['table']})
    return result

def system_profile_getter(r):
    return {rti['publisher']:rti['name'] for rti in r._recordtype_info.values() if rti['name'][0:2] not in ['GP','US','DS'] and 'publisher' in rti and rti['publisher'] and rti['publisher'][0:2]!='GR'}
