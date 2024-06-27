entity_key_selector = {
'group': ['GPBD','group name'],
'user': ['USBD','user ID'],
'dataset': ['DSBD',['profile','dataset name match']],
'general resource': ['GRBD','class',['profile','resource match']],
'system profile': ['*','profile']
}
entity_data_selector = {
'group': '''OWNER_ID SUPGRP_ID UNIVERSAL INSTALL_DATA
            NOTERMUACC UACC MODEL CREATE_DATE'''.split(),
'user': '''PROGRAMMER OWNER_ID DEFGRP_ID
           SPECIAL OPER AUDITOR ROAUDIT
           REVOKE REVOKE_DATE RESUME_DATE
           ATTRIBS UAUDIT 
           MFA_FALLBACK REVOKE_CNT
           PWD_INTERVAL PWD_DATE PWD_GEN PWD_ASIS PWD_ALG
           PHR_INTERVAL PHR_DATE PHR_GEN PHR_ALG 
           PWDENV_EXISTS PPHENV_EXISTS
           CREATE_DATE LASTJOB_TIME LASTJOB_DATE
           INSTALL_DATA
           ADSP GRPACC NOPWD OIDCARD
           MODEL 
           SECLEVEL SECLABEL'''.split(),
'dataset': '''UACC IDSTAR_ACCESS ALL_USER_ACCESS WARNING ERASE 
              GENERIC VOL OWNER_ID NOTIFY_ID 
              AUDIT_LEVEL AUDIT_OKQUAL AUDIT_FAQUAL 
              GAUDIT_LEVEL GAUDIT_OKQUAL GAUDIT_FAQUAL
              LEVEL SECLEVEL SECLABEL INSTALL_DATA
              CREATE_DATE LASTCHG_DATE'''.split(),
'general resource': '''UACC IDSTAR_ACCESS ALL_USER_ACCESS WARNING
                       GENERIC OWNER_ID NOTIFY_ID APPL_DATA
                       AUDIT_LEVEL AUDIT_OKQUAL AUDIT_FAQUAL 
                       GAUDIT_LEVEL GAUDIT_OKQUAL GAUDIT_FAQUAL
                       LEVEL SECLEVEL SECLABEL INSTALL_DATA
                       CREATE_DATE LASTCHG_DATE'''.split()
}

def system_profile_getter(r):
    return {rti['publisher']:rti['name'] for rti in r._recordtype_info.values() if rti['name'][0:2] not in ['GP','US','DS'] and 'publisher' in rti and rti['publisher'] and rti['publisher'][0:2]!='GR'}

