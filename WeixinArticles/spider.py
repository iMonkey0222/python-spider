from urllib.parse import urlencode
from lxml.etree import XMLSyntaxError
from requests.exceptions import ConnectionError
import requests
from pyquery import PyQuery as pq
import pymongo

from config import *

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

base_url = 'https://weixin.sogou.com/weixin?'

headers = {
    'Cookie': 'CXID=DF1F2AE56903B8B6289106D60E0C1339; SUID=F5959E3D8483920A000000005BCEB8CD; sw_uuid=3544458569; ssuid=8026096631; pex=C864C03270DED3DD8A06887A372DA219231FFAC25A9D64AE09E82AED12E416AC; SUV=00140F4F78C27EE25BF168CF5C981926; ad=p7R@vkllll2bio@ZlllllVsE@EclllllNBENLlllll9lllllpA7ll5@@@@@@@@@@; IPLOC=CN4110; ABTEST=2|1543456547|v1; weixinIndexVisited=1; sct=1; JSESSIONID=aaaXtNmDWRk5X5sEsy6Cw; PHPSESSID=lfgarg05due13kkgknnlbh3bq7; SUIR=EF72CF750D0876CFF631992E0D94BE34;',
    'Host': 'weixin.sogou.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
}

proxy = None

def get_proxy():
    try:
        response = requests.get(PROXY_POOL_URL)
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError:
        return None

def get_html(url, count=1):
    print('Crawling', url)
    print('Trying Count', count)
    global proxy
    if count >= MAX_COUNT:
        print('Tried Too Many Counts')
        return None
    try:
        if proxy:
            proxies = {
                'http': 'http://' + proxy
            }
            # allow_redirects=False:禁止浏览器自动处理302跳转
            response = requests.get(url, allow_redirects=False, headers=headers, proxies=proxies)
        else:
            response = requests.get(url, allow_redirects=False, headers=headers)
        if response.status_code == 200:
            return response.text
        if response.status_code == 302:
            # Need Proxy
            print('302')
            proxy = get_proxy()
            if proxy:
                print('Using Proxy', proxy)
                return get_html(url)
            else:
                print('Get Proxy Failed')
                return None
    except ConnectionError as e:
        print('Error Occurred', e.args)
        proxy = get_proxy()
        count += 1
        return get_html(url, count)


def get_index(keyword, page):
    data = {
        'query': keyword,
        'type': 2,
        'page': page
    }
    queries = urlencode(data)
    url = base_url + queries
    html = get_html(url)
    return html

def parse_index(html):
    doc = pq(html)
    items = doc('.news-box .news-list li .txt-box h3 a').items()
    for item in items:
        yield item.attr('href')

def get_detail(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
    except ConnectionError:
        return None

def parse_detail(html):
    try:
        doc = pq(html)
        title = doc('.rich_media_title').text()
        content = doc('.rich_media_content ').text()
        date = doc('#publish_time').text()
        nickname = doc('.rich_media_meta_list .rich_media_meta_nickname').text()
        wechat = doc('#activity-name').text()
        return {
            'title': title,
            'content': content,
            'date': date,
            'nickname': nickname,
            'wechat': wechat
        }
    except XMLSyntaxError:
        return None

def save_to_mongo(data):
    if db['articles'].update({'title': data['title']}, {'$set': data}, True):
        print('Saved to Mongo', data['title'])
    else:
        print('Saved to Mongo Failed', data['title'])

def main():
    for page in range(1, 101):
        html = get_index(KEYWORD, page)
        if html:
            article_urls = parse_index(html)
            for article_url in article_urls:
                article_html = get_detail(article_url)
                if article_html:
                    article_data = parse_detail(article_html)
                    print(article_data)
                    if article_data:
                        save_to_mongo(article_data)

if __name__ == "__main__":
    main()
