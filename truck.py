import datetime
import time
import rfc822
from django.conf import settings
from urllib2 import Request, urlopen, URLError, HTTPError
from urllib import urlencode
import re 
import string
try:
  import django.utils.simplejson as json
except:
  import json
from django.core.cache import cache

from tagging.models import Tag

from foodtruck.models import *
from foodtruck.tokens import *

import oauth2 as oauth

def fetch_json(url, service, list_key=None):
    fetched = urlopen(url).read()
    data = json.loads(fetched)
    if list_key:
        data = data[list_key]
    return data
    
def oauth_req(url, key, secret, http_method="GET", post_body=None,http_headers=None):
	consumer = oauth.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
	token = oauth.Token(key=key, secret=secret)
	client = oauth.Client(consumer, token)
	resp, content = client.request(
		url,
		method=http_method,
		body=post_body,
		headers=http_headers,
		force_auth_header=True
	)
	return content

def get_all_tweets():
  from dateutil.parser import parse, tz
  url = LIST_URL
  HERE = tz.tzlocal()
  if cache.get('truck_tweets'):
    tweets = cache.get('truck_tweets')
  else:
    tweets = []
    all_tweets = oauth_req(url, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    data = json.loads(all_tweets)
    for t in data:
      m = dict(
      name = t['user']['screen_name'],
      pic_url = t['user']['profile_image_url'],
      text = t['text'],
      timestamp = parse(t['created_at']).astimezone(HERE),
      url = 'http://twitter.com/'+t['user']['screen_name']+'/statuses/'+str(t['id']),
      ) 
      tweets += [m]
    cache.set('truck_tweets',tweets, 62)
  return tweets 


def filter_trucks(hood):
  tweets = get_all_tweets()  
  n = Hood.objects.get(id=hood)
  tags = n.tags.all()
  filtered = {'hood':n.name, 'tags':tags}
  filtered['tweets'] = []
  for t in tweets:
    for w in tags:
      if string.find(t['text'].lower(), w.name.lower()) > 0:  
        filtered['tweets'] += [t]
        break
  cache.set((('filtered_%s' % hood)), filtered, 62)
  return filtered
  
  
def get_truck_names():
  p = open('truck.cursor','r')
  try: last_cursor = int(p.read())
  except: last_cursor=1353949495935930905 # this is just the last cursor number i looked up, to save on API calls -- can change.
  p.close()

  url = LIST_MEMBERS_URL
  get_truck_list = oauth_req(url, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
  truck_list = json.loads(get_truck_list)
  all_trucks = truck_list['users']
  cursor = truck_list['next_cursor']
  f = open('truck.cursor','w')
  f.write(str(cursor))
  f.close

  while cursor > last_cursor:
    truck_url = LIST_MEMBERS_URL +'?cursor=' + str(cursor)
    get_truck_list = oauth_req(truck_url,OAUTH_TOKEN,OAUTH_TOKEN_SECRET)
    truck_list = json.loads(get_truck_list)
    all_trucks += truck_list['users']
    cursor = truck_list['next_cursor']
  for truck in all_trucks:
    description=truck['description'] or ''
    truck_url= truck['url'] or 'http://twitter.com/'+truck['screen_name']
    profile_icon= truck['profile_image_url'] or ''
    real_name=truck['name'] or truck['screen_name']
    t = Truck.objects.get_or_create(id_str__exact=truck['id_str'], defaults = {'name':truck['screen_name'], 'description':description, 'profile_icon':profile_icon, 'truck_url':truck_url, 'geo_enabled':truck['geo_enabled'], 'real_name':real_name, 'id_str':truck['id_str']})


if __name__=='__main__':
    import sys
    try:
        func = sys.argv[1]
    except: func = None
    if func:
        try:
            exec 'print %s' % func
        except:
            print "Error: incorrect syntax '%s'" % func
    else: print "Please name your function"
