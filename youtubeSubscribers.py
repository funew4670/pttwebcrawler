#get youtube subscription
import os
import sys
import json
import requests
import time
import datetime
import argparse
import logging
import logging.handlers
import subprocess
import re
import urllib.request
import urllib.parse
import urllib.error

#api key required
myapikey=""
myuserid=""

#logging
logger = logging.getLogger('youtube_subscription')
logger.setLevel(logging.DEBUG)

# create file handler which logs even debug messages
fh = logging.handlers.TimedRotatingFileHandler('youtube_subscription.log', when='midnight', interval=1, backupCount=7)
fh.setLevel(logging.DEBUG)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

#get youtube subscription
def get_subscription(youtube_api_key, youtube_channel_id, page_token):
    logger.info('get_subscription')
    url = 'https://www.googleapis.com/youtube/v3/subscriptions?part=snippet&channelId=' + youtube_channel_id + '&key=' + youtube_api_key
    if page_token != None:
        url += '&pageToken=' + page_token
    logger.debug('url: ' + url)
    try:
        response = requests.get(url)
        logger.debug('response: ' + response.text)
        return response.json()
    except Exception as e:
        logger.error('get_subscription error: ' + str(e))
        return None


#get youtube video
def get_video(youtube_api_key, youtube_video_id):
    logger.info('get_video')
    url = 'https://www.googleapis.com/youtube/v3/videos?part=snippet&maxResults=25&id=' + youtube_video_id + '&key=' + youtube_api_key
    logger.debug('url: ' + url)
    try:
        response = requests.get(url)
        logger.debug('response: ' + response.text)
        return response.json()
    except Exception as e:
        logger.error('get_video error: ' + str(e))
        return None



nextPageToken = ""
pageToken=""
jsonconcatenated = {}

response = get_subscription(myapikey,myuserid,"")
items = response['items']
jsonconcatenated = items
nextPageToken = response['nextPageToken']


while nextPageToken is not None:
    response = get_subscription(myapikey,myuserid,nextPageToken)
    items = response['items']
    #add nextpagetoken key error prevent
    if 'nextPageToken' in response:
        nextPageToken = response['nextPageToken']
    else:
        nextPageToken = ""
    #concatenate json
    jsonconcatenated = jsonconcatenated + items    
    time.sleep(10)

with open('subscription.json', 'w',encoding='utf-8') as f:
    json.dump(jsonconcatenated, f, ensure_ascii=False,indent=4)












