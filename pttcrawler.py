from requests_html import HTML
import requests


def parse_article_entries(doc):

    html = HTML(html=doc)

    post_entries = html.find('div.r-ent')

    return post_entries

def fetch(url):

    response = requests.get(url)

    response = requests.get(url, cookies={'over18': '1'})

    return response

def parse_article_meta(entry):

    meta = {'title': entry.find('div.title', first=True).text,
        'push': entry.find('div.nrec', first=True).text,
        'date': entry.find('div.date', first=True).text,
        'author': entry.find('div.author', first=True).text,
        'link': entry.find('div.title > a', first=True).attrs['href'],
    }
    try:
        meta['author'] = entry.find('div.author', first=True).text
        meta['link'] = entry.find('div.title > a', first=True).attrs['href']
    except AttributeError:
        if '(本文已被刪除)' in meta['title']:
            match_author = re.search('\[(\w*)\]', meta['title'])
            if match_author:
                meta['author'] = match_author.group(1)
        elif re.search('已被\w*刪除', meta['title']):
            match_author = re.search('\<(\w*)\>', meta['title'])
            if match_author:
                meta['author'] = match_author.group(1)
    return meta
    
    return meta


url = 'https://www.ptt.cc/bbs/movie/index.html'

resp = fetch(url)  # step-1

post_entries = parse_article_entries(resp.text)  # step-2


for entry in post_entries:
    meta = parse_article_meta(entry)
    print(meta)  # result of setp-3

            
