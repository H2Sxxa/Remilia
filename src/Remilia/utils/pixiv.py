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


import asyncio
import json
import re
import socket
from typing import Any, Dict, List

import aiohttp
from aiohttp import ClientTimeout
from aiohttp.abc import AbstractResolver

'''
come from pixiv_async

https://pypi.org/project/PixivPy-Async/

LICENSE: https://github.com/Mikubill/pixivpy-async/blob/master/LICENSE UNLICENSE
'''
class ByPassResolver(AbstractResolver):

    def __init__(self, endpoints=None, force_hosts=True):
        self.endpoints = [
            "https://1.0.0.1/dns-query",
            "https://1.1.1.1/dns-query",
            "https://[2606:4700:4700::1001]/dns-query",
            "https://[2606:4700:4700::1111]/dns-query",
            "https://cloudflare-dns.com/dns-query",
        ] if endpoints is None else endpoints
        self.force_hosts = force_hosts

    async def resolve(self, host: str, port, family=socket.AF_INET) -> List[Dict[str, Any]]:

        new_host = host
        if self.force_hosts and host in ["app-api.pixiv.net", "public-api.secure.pixiv.net", "www.pixiv.net", "oauth.secure.pixiv.net"]:
            new_host = "www.pixivision.net"

        done, pending = await asyncio.wait([asyncio.create_task(
            self._resolve(endpoint, new_host, family))
            for endpoint in self.endpoints], return_when=asyncio.FIRST_COMPLETED)

        ips = await self.read_result(done.union(pending))
        for future in pending:
            future.cancel()

        if len(ips) == 0:
            raise Exception("Failed to resolve {}".format(host))

        result = []
        for i in ips:
            result.append({
                "hostname": "",
                "host": i,
                "port": port,
                "family": family,
                "proto": 0,
                "flags": socket.AI_NUMERICHOST,
            })
        return result

    async def read_result(self, tasks: List[asyncio.Task]) -> List[str]:
        if len(tasks) == 0:
            return []
        task = tasks.pop()
        
        try:
            await task
            return task.result()
        except Exception as e:
            #print("caught:", repr(e))
            return await self.read_result(tasks)
            
    async def close(self) -> None:
        pass

    async def parse_result(self, hostname, response) -> List[str]:
        data = json.loads(response)
        if data['Status'] != 0:
            pass
            #raise Exception("Failed to resolve {}".format(hostname))

        # Pattern to match IPv4 addresses 
        pattern = re.compile(
            r"((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.){3}(1\d\d|2[0-4]\d|25[0-5]|[1-9]\d|\d)")
        result = []

        for i in data["Answer"]:
            ip = i["data"]

            if pattern.match(ip) is not None:
                result.append(ip)

        return result

    async def _resolve(self, endpoint, hostname, family, timeout=5) -> List[str]:

        params = {
            "name": hostname,
            "type": "AAAA" if family == socket.AF_INET6 else "A",
            "do": "false",
            "cd": "false",
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, params=params, headers={"accept": "application/dns-json"}, timeout=ClientTimeout(total=timeout)) as resp:
                    if resp.status == 200:
                        return await self.parse_result(hostname, await resp.text())
                    else:
                        pass
                        #raise Exception("Failed to resolve {} with {}: HTTP Status {}".format(
                        #    hostname, endpoint, resp.status))
        except:
            pass

class PixivClient:
    def __init__(self, limit=30, timeout=10, env=False, internal=False, proxy=None, bypass=False):
        """
            When 'env' is True and 'proxy' is None, possible proxies will be
            obtained automatically (wrong proxy may be obtained).

            When 'proxy' is not None, it will force the proxy to be used and
            'env' will have no effect.

            proxy <str> is used for a single proxy with a url:
                'socks5://user:password@127.0.0.1:1080'

            If you want to use proxy chaining, read https://github.com/romis2012/aiohttp-socks.

        """

        kwargs = {'limit_per_host': limit}

        if bypass:
            import ssl

            ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ssl_ctx.check_hostname = False
            ssl_ctx.verify_mode = ssl.CERT_NONE

            kwargs.update({'ssl': ssl_ctx, 'resolver': ByPassResolver()})

        if proxy:
            try:
                from aiohttp_socks import ProxyConnector
                self.conn = ProxyConnector.from_url(proxy, **kwargs)
                _flag = False
            except ModuleNotFoundError as e:
                if proxy.startswith('socks'):
                    raise e
                else:
                    self.conn = aiohttp.TCPConnector(**kwargs)
                    _flag = True
        else:
            self.conn = aiohttp.TCPConnector(**kwargs)

        self.internal = internal

        self.client = aiohttp.ClientSession(
            connector=self.conn,
            timeout=aiohttp.ClientTimeout(total=timeout),
            trust_env=env,
        )

        if proxy and _flag:
            from functools import partial
            self.client.head = partial(self.client.head, proxy=proxy)
            self.client.get = partial(self.client.get, proxy=proxy)
            self.client.post = partial(self.client.post, proxy=proxy)

    def start(self):
        return self.client

    async def close(self):
        await asyncio.sleep(0)
        await self.client.close()

    async def __aenter__(self):
        return self.client

    async def __aexit__(self, exc_type, exc, tb):
        await asyncio.sleep(0)
        await self.client.close()