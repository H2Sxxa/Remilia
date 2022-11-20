import subprocess

'''
@Author H2Sxxa

You must download a gss from https://github.com/shadowsocks/go-shadowsocks2/releases and use it as gsspath

'''


class ProcessHandle:
    def __init__(self,path:str,log_file:str,*args) -> None:
        with open(log_file,"w",encoding="utf-8") as f:
                self.prcs=subprocess.Popen(
                        args=(path,*args),
                        shell=True,
                        stdout=f,
                        stderr=f,
                )
class Client:
    def __init__(self,gsspath:str,log_file:str="shadowsocks2.log",*args) -> None:
        '''
        ## See https://github.com/shadowsocks/go-shadowsocks2
        Usage of shadowsocks2-win64.exe:
        -c string
                client connect address or url
        -cipher string
                available ciphers: AEAD_AES_128_GCM AEAD_AES_256_GCM AEAD_CHACHA20_POLY1305 (default "AEAD_CHACHA20_POLY1305")
        -key string
                base64url-encoded key (derive from password if empty)
        -keygen int
                generate a base64url-encoded random key of given length in byte
        -password string
                password
        -plugin string
                Enable SIP003 plugin. (e.g., v2ray-plugin)
        -plugin-opts string
                Set SIP003 plugin options. (e.g., "server;tls;host=mydomain.me")
        -redir string
                (client-only) redirect TCP from this address
        -redir6 string
                (client-only) redirect TCP IPv6 from this address
        -s string
                server listen address or url
        -socks string
                (client-only) SOCKS listen address
        -tcp
                (server-only) enable TCP support (default true)
        -tcpcork
                coalesce writing first few packets
        -tcptun string
                (client-only) TCP tunnel (laddr1=raddr1,laddr2=raddr2,...)
        -u	(client-only) Enable UDP support for SOCKS
        -udp
                (server-only) enable UDP support
        -udptimeout duration
                UDP tunnel timeout (default 5m0s)
        -udptun string
                (client-only) UDP tunnel (laddr1=raddr1,laddr2=raddr2,...)
        -verbose
                verbose mode
        '''
        self.ph=ProcessHandle(gsspath,log_file,*args)
        
    @property
    def process(self):
        return self.ph.prcs

    def wait(self):
        self.process.wait()