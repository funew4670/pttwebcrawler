from requests_html import HTML
import requests
import time
import urllib.parse
import re

def parse_article_entries(doc):

    html = HTML(html=doc)

    post_entries = html.find('div.r-ent')

    return post_entries

def fetch(url,params):

    #response = requests.get(url,params)
    
    response = requests.get(url,params=params, cookies={'over18': '1'})

    return response

def fetch_content(url):

    #response = requests.get(url,params)
    
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


def parse_article_content(doc):
    html=HTML(html=doc)
    entry = html.find('div.bbs-screen')
    content = entry[0].text
    content = content.replace("【1.請注意兩日內僅能徵、賣、估各1篇，切勿2PO or 以上   】","")
    content = content.replace("【2.非本板討論範圍請勿PO文(詳細規定請看置底板規)       】","")
    content = content.replace("【3.確定無誤再發文，發現有誤請大T修標題大E修內文       】","")
    content = content.replace("【4.無用的整行文字 (例此行以上) 可按「Ctrl+Ｙ」刪除整行】","")
    content = content.replace("【5.賣出後勿清空內文、標題、價格，違者水桶2個月        】","")
    content = content.replace("【6.勿刪除他人推文，違者退文並水桶1個月                】","")
    content = content.replace("【7.請 先 按 「Ctrl+Ｖ」!!  還原色碼後，方可正常編輯   】","")
    content = content.replace("(沒有明確價格、賣出後清空價格，水桶2個月)","")
    content = content.replace("(購買日期、保固有無、使用期間、新舊程度)","")
    content = content.replace("(官方規格、網拍連結、實物品樣照片)","")
    content = content.replace("(自取、面交、郵寄、宅急便)","")
    content = content.replace("(限面交者請交待詳細區域地點!!)","")
    content = content.replace("(站內信、手機、即時通訊軟體、如何稱呼)","")
    return content

def parse_article_content2(doc) :
    result = re.split("\x0a",doc)
    for a in result:
        escapeString = "※推→"
        if not any(x in escapeString for x in a):
            print(a)
        else:
            if (a.find("--") != -1):
                s2=a.split('--')[0]    
                parse_article_content3(s2)
            else:
                #if there is "--" dont parse
                continue
    return None

def parse_article_content3(s2) :
    #print(doc)
    if not s2:
        return None

    regex = r"(?<=◎硬體型號：)(.+)(?=◎欲售價格：)"
    if re.search(regex,s2) != None :
        p1= re.split(regex,s2)
        print("◎硬體型號：\n")
        print(p1[1]+"\n")
    regex = r"(?<=◎欲售價格：)(.+)(?=◎品樣狀況：)"
    if re.search(regex,s2) != None :
        p2= re.split(regex,s2)
        print("◎欲售價格：\n")
        print(p2[1]+"\n")
    regex = r"(?<=◎品樣狀況：)(.+)(?=◎參考網頁：)"
    if re.search(regex,s2) != None :
        p3= re.split(regex,s2)
        print("◎品樣狀況：\n")
        print(p3[1]+"\n")
    regex = r"(?<=◎參考網頁：)(.+)(?=◎交易方式：)"
    if re.search(regex,s2) != None :
        p4= re.split(regex,s2)
        print("◎參考網頁：\n")
        print(p4[1]+"\n")
    regex = r"(?<=◎交易方式：)(.+)(?=◎交易地區：)"
    if re.search(regex,s2) != None :
        p5= re.split(regex,s2)
        print("◎交易方式：\n")
        print(p5[1]+"\n")
    regex = r"(?<=◎交易地區：)(.+)(?=◎聯絡方式：)"
    if re.search(regex,s2) != None :
        p6= re.split(regex,s2)
        print("◎交易地區：\n")
        print(p6[1]+"\n")
    regex = r"(?<=◎聯絡方式：)(.+)"
    if re.search(regex,s2) != None :
        p7= re.split(regex,s2)
        print("◎聯絡方式：\n")
        print(p7[1]+"\n")
    time.sleep(1)

    return None


url = 'https://www.ptt.cc/bbs/HardwareSale/search'
params = ["1070ti"]

for para in params:
    resp = fetch(url,{'q':para})  # step-1
    post_entries = parse_article_entries(resp.text)  # step-2
    for entry in post_entries:
        meta = parse_article_meta(entry)
        if "賣" not in meta['title'] :
            continue
        print(meta['title'])  # result of setp-3
        page_url = urllib.parse.urljoin('https://www.ptt.cc/bbs/HardwareSale/',meta['link'])
        print(page_url)
        resp_c = fetch_content(page_url)
        #print(resp_c.text)
        content = parse_article_content(resp_c.text)
        parse_article_content2(content)
        #print(content)
        #meta['content']= parse_article_content(resp_c.text).text
        #print(meta['content'])
        time.sleep(1)

