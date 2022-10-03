
def buildheader(token):
    return {
    'App-OS': 'ios',
    'App-OS-Version': '12.2',
    'App-Version': '7.6.2',
    'User-Agent': 'PixivIOSApp/7.6.2 (iOS 12.2; iPhone9,1)',
    'Authorization': 'Bearer %s' % token
    }


async def getAuth(refresh_token:str=None):
    import pixivpy_async
    async with pixivpy_async.PixivClient(bypass=True) as clt:
        api=pixivpy_async.AppPixivAPI(client=clt)
        if refresh_token:
            auth=await api.login(refresh_token=refresh_token)
        else:
            auth=await api.login_web()
        return auth

def getHeader(auth:dict):
    '''
    use getAuth before it
    '''
    return buildheader(auth["access_token"])
    