def connectAttributes(df):
    '''insert a column ``attribs`` into connectData with a summary of privileges and authorities'''
    map_priv = {'GRP_SPECIAL':'S',
                'GRP_OPER':'O',
                'GRP_AUDIT':'A',
                'REVOKE':'R'}
    map_auth = {'CONNECT':'connect',
                'JOIN':'join',
                'CREATE':'create'}
    df.insert(3,'attribs','')
    for c,f in map_priv.items():
        df.attribs = df.attribs.where(df[c]=='NO',df.attribs+f)
    df.attribs = df.attribs.where(df.attribs=='',df.attribs+' ')
    for v,f in map_auth.items():
        df.attribs = df.attribs.where(df.GPMEM_AUTH!=v,df.attribs+f)
    df.attribs = df.attribs.where(df.attribs!='','use')
    return df
