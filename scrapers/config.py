from ruamel.yaml import YAML

yaml = YAML()
config = yaml.load(open('config.yml'))

dbconf = config['db']['dev']
proxyconf = config['proxy']

logconf = config['logs']


def get_proxies():
    proxy_user = proxyconf['user']
    proxy_pass = proxyconf['pw']
    proxies = {
        'http': f'http://{proxy_user}:{proxy_pass}@zproxy.lum-superproxy.io:22225',
        'https': f'http://{proxy_user}:{proxy_pass}@zproxy.lum-superproxy.io:22225'
        }
    return proxies

