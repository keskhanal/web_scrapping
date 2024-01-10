from ruamel.yaml import YAML
from fp.fp import FreeProxy

yaml = YAML()
config = yaml.load(open('config.yml'))
dbconf = config['db'][config['env']]
proxyconf = config['proxy']
logconf = config['logs']
scraper_auth = config['scraper_auth']

def get_proxies():
    proxy_user = proxyconf['user']
    proxy_pass = proxyconf['pw']
    proxies = {
        'http': f'http://{proxy_user}:{proxy_pass}@zproxy.lum-superproxy.io:22225',
        'https': f'https://{proxy_user}:{proxy_pass}@zproxy.lum-superproxy.io:22225'
        }
    # proxy = FreeProxy(anonym=True, https=False).get()
    # print(proxy)
    # proxies = {
    #     'http': proxy,
    #     'https': proxy
    #     }
    # print(proxies)
    return proxies

