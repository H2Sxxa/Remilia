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

class AioBypass:
    '''
    A class adopted from https://rainchan.win/2021/08/07/%E5%85%B3%E4%BA%8EPixiv%E5%92%8CSNI%E7%9A%84%E9%82%A3%E4%BA%9B%E4%BA%8B/
    '''
    @staticmethod
    def BypassClient(*args,**kwargs):
        '''
```python
import asyncio
from Remilia.utils.net import pixiv
async def test():
    async with pixiv.AioBypass.BypassClient() as client:
        async with client.get("https://www.pixiv.net/artworks/100275478") as resp:
            return await resp.text()
    
loop=asyncio.get_event_loop()
cnt=loop.run_until_complete(test())
print(cnt)
```
        '''
        import ssl,aiohttp
        ssl_ctx = ssl.SSLContext()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        connector = aiohttp.TCPConnector(ssl=ssl_ctx, resolver=AioBypass.ByPassResolver())
        client = aiohttp.ClientSession(*args,**kwargs,connector=connector)
        return client

    from aiohttp.abc import AbstractResolver
    @staticmethod
    class ByPassResolver(AbstractResolver):
        from typing import List,Dict,Any
        async def resolve(self, host: str, port: int, family: int) -> List[Dict[str, Any]]:
            import socket
            new_host = host
            if host == "app-api.pixiv.net":
                new_host = "www.pixivision.net"
            if host == "www.pixiv.net":
                new_host = "www.pixivision.net"

            ips = await self.require_appapi_hosts(new_host)
            result = []

            for i in ips:
                result.append({
                    "hostname": "",
                    "host": i,
                    "port": port,
                    "family": family,
                    "proto": 0,
                    "flags": socket.AI_NUMERICHOST | socket.AI_NUMERICSERV,
                })
            return result

        async def close(self) -> None:
            pass

        async def require_appapi_hosts(self, hostname, timeout=3) -> List[str]:
            """
            通过 Cloudflare 的 DNS over HTTPS 请求真实的 IP 地址。
            """
            import aiohttp,json,re
            URLS = (
                "https://cloudflare-dns.com/dns-query",
                "https://1.0.0.1/dns-query",
                "https://1.1.1.1/dns-query",
                "https://[2606:4700:4700::1001]/dns-query",
                "https://[2606:4700:4700::1111]/dns-query",
            )
            params = {
                "ct": "application/dns-json",
                "name": hostname,
                "type": "A",
                "do": "false",
                "cd": "false",
            }

            for url in URLS:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, params=params, timeout=timeout) as rsp:
                            response = await rsp.text()
                            obj = json.loads(response)
                            pattern = re.compile(
                                "((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.){3}(1\d\d|2[0-4]\d|25[0-5]|[1-9]\d|\d)")
                            result = []
                            for i in obj["Answer"]:
                                ip = i["data"]

                                if pattern.match(ip) is not None:
                                    result.append(ip)
                            #print(result)
                            return result

                except Exception as e:
                    #import traceback
                    #traceback.print_exc()
                    pass
