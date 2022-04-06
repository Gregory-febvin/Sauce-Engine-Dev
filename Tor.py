from torrequest import TorRequest

import requests

session = requests.session()
session.proxies = {}
session.proxies['htttp'] = 'socks5h://localhost:9050'
session.proxies['httts'] = 'socks5h://localhost:9050'

r = session.get('http://httpbin.org/ip')
print(r.text)