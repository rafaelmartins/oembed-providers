#!/usr/bin/env python
# coding: utf-8

from bs4 import BeautifulSoup
from bs4.element import Tag
import json
import re
import requests
import sys

WEBSITE_URL = 'http://oembed.com/'
DEFAULT_SCHEMES = {  # oembed.com does not provides youtube schemes :(
    'YouTube': [u'http://youtube.com/*',
                u'https://youtube.com/*',
                u'http://youtu.be/*']
}

re_url_scheme = re.compile(r'.*url *scheme.*', re.I)
re_endpoint = re.compile(r'.*endpoint.*', re.I)


def parse_website():
    r = requests.get(WEBSITE_URL)
    if not r.ok:
        raise RuntimeError('Failed to access webpage: %s' % WEBSITE_URL)
    page = BeautifulSoup(r.content)
    capture = False
    providers = []
    provider = None
    for elem in page.find(id='main'):
        if not isinstance(elem, Tag):
            continue
        if elem.name == 'a':
            if elem['id'] == 'section7.1':
                capture = True
            if elem['id'] == 'section7.2':
                capture = False
            continue
        if not capture:
            continue
        if elem.name == 'p':
            pieces = list(elem.children)
            provider = {'name': pieces[0].strip('( '),
                        'url': elem.find('a')['href'].strip()}
        elif elem.name == 'ul':
            schemes = []
            endpoint = None
            for li in elem.find_all('li'):
                pieces = list(li.children)
                if re_url_scheme.match(pieces[0]):
                    scheme = li.find('code')
                    if scheme is None:
                        continue
                    schemes.extend(scheme.contents)
                if re_endpoint.match(pieces[0]):
                    endpoint_elem = li.find('code')
                    if endpoint_elem is None:
                        continue
                    endpoint = endpoint_elem.contents[0].split('(')[0].strip()
                    endpoint = endpoint.split(' ')[0]
            if len(schemes) == 0:
                if provider['name'] in DEFAULT_SCHEMES:
                    schemes = DEFAULT_SCHEMES[provider['name']]
                else:
                    continue
            if endpoint is None:
                continue
            provider.update({'schemes': schemes, 'endpoint': endpoint})
            providers.append(provider)
    return providers


if __name__ == '__main__':
    json.dump(parse_website(), sys.stdout, indent=4)

