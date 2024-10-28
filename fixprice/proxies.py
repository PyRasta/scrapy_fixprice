import re
import random

import requests


def get_random_proxy():
    with open('proxies.txt') as file:
        proxies = file.readlines()
    proxies = list(map(lambda x: x.replace('\n', ''), proxies))
    return random.choice(proxies)


def get_proxies():
    with open('proxies.txt') as file:
        proxies = file.readlines()
    proxies = list(map(lambda x: x.replace('\n', ''), proxies))
    return proxies


def load_proxy(proxy):
    auth_required = re.search(':.*[@:].*:', proxy)
    if auth_required:
        proxys = proxy.replace('@', ':')
        proxys = proxys.split(':')
        PROXY_HOST = proxys[2]
        PROXY_PORT = proxys[-1]
        PROXY_USER = proxys[0]
        PROXY_PASS = proxys[1]
        return f'http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}'
    else:
        return False


def load_proxy_selenium(proxy):
    auth_required = re.search(':.*[@:].*:', proxy)
    if auth_required:
        proxys = proxy.replace('@', ':')
        proxys = proxys.split(':')
        PROXY_HOST = proxys[2]
        PROXY_PORT = proxys[-1]
        PROXY_USER = proxys[0]
        PROXY_PASS = proxys[1]
        prx = {
            'url': f'http://{PROXY_HOST}:{PROXY_PORT}',
            'username': PROXY_USER,
            'password': PROXY_PASS
        }
        return prx
    else:
        return False


def load_proxy_just(proxy):
    auth_required = re.search(':.*[@:].*:', proxy)
    if auth_required:
        proxys = proxy.replace('@', ':')
        proxys = proxys.split(':')
        PROXY_HOST = proxys[2]
        PROXY_PORT = proxys[-1]
        PROXY_USER = proxys[0]
        PROXY_PASS = proxys[1]
        prx = {
            'http': f'http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}',
            'https': f'http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}',
        }
        return prx
    else:
        return False


def check_proxy(proxy):
    proxy = load_proxy_just(proxy)
    if proxy:
        try:
            r = requests.get('http://api.ipify.org', proxies=proxy, timeout=5)
        except:
            r = False
        if r:
            return True
    return False
