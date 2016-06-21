import re
import execjs
import requests

STATION_FROM_ID = 2200001
STATION_FROM_NAME = '%D0%9A%D0%B8%D1%97%D0%B2'

STATION_TILL_ID = 2210800
STATION_TILL_NAME = '%D0%97%D0%B0%D0%BF%D0%BE%D1%80%D1%96%D0%B6%D0%B6%D1%8F%201'
BASE_URL = 'http://booking.uz.gov.ua/ru/'

STATION_URL = BASE_URL + 'purchase/station/'

SEARCH_URL = BASE_URL + 'purchase/search/'

BASE_HEADERS = {
    'Connection': 'keep-alive',
    'Host': 'booking.uz.gov.ua',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:36.0) Gecko/20100101 Firefox/36.0',
}

SEARCH_HEADERS = {
    'GV-Ajax': 1,
    'GV-Referer': BASE_URL,
    'GV-Screen': '1366x768',
    'GV-Unique-Host': 1,
    'Origin': 'http://booking.uz.gov.ua',
    'Referer': BASE_URL,
}

TOKEN_RE = re.compile('({}.*{})'.format(re.escape('$$_='), re.escape(')())();')))


def get_cookies_and_token():
    url = BASE_URL
    headers = BASE_HEADERS
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        return
    matches = TOKEN_RE.findall(resp.text)
    if not matches:
        return
    if len(matches) > 1:
        return
    js_obfuscated = matches[0]
    js_fake_storage = 'localStorage = {token: undefined, setItem: function (key, value) {this.token = value}}'
    js_code = (
        'function getToken() {{\n'
        '\t{};\n'
        '\t{};\n'
        '\treturn localStorage.token;\n'
        '}}'
    ).format(js_fake_storage, js_obfuscated)
    return resp.cookies, execjs.compile(js_code).call('getToken')

def get_trains(dep_date, cookies, token):
    data = {
        'station_id_from': STATION_FROM_ID,
        'station_id_till': STATION_TILL_ID,
        'station_from': STATION_FROM_NAME,
        'station_till': STATION_TILL_NAME,
        'date_dep': dep_date,
        'time_dep': '00:00',
        'time_dep_till': '',
        'another_ec': 0,
        'search': '',
    }
    headers = dict(BASE_HEADERS, **SEARCH_HEADERS)
    headers['GV-Token'] = token
    resp = requests.post(SEARCH_URL, data, headers=headers, cookies=cookies)
    if resp.status_code != 200:
        return

    return resp.json()['value']


def find_tickets(dep_date):
    cookies, token = get_cookies_and_token()
    return get_trains(dep_date, cookies, token)
