#!/usr/bin/python

import urllib
from bs4 import BeautifulSoup
import datetime
import json
import re
import subprocess
import sys

if len(sys.argv) < 4:
	print 'Usage: jsonfile title url'
	exit()

(jsonfile,title,url) = sys.argv[1:4]
movieid = re.sub('https*://www.nicovideo.jp/watch/', '', url)

# read json
file = open(jsonfile, 'r')
data = json.load(file)
file.close()

userComments = r'([0-9]*) UserPlays, ([0-9]*) UserComments.*'
# userComments = r'.*viewCount&quot;:([0-9]*),.*commentCount&quot;:([0-9]*).*'

# get HTML
url = 'http://www.nicovideo.jp/watch/%s' % movieid
html = urllib.urlopen(url)
soup = BeautifulSoup(html, "html.parser")

# get UserComments count
playCount = None
commentCount = None
metas = soup.find_all('meta', attrs={'itemprop':'interactionCount'})
for meta in metas:
	match = re.search(userComments, meta.get('content'))
	if match != None:
		playCount = match.group(1)
		commentCount = match.group(2)

# update count
if commentCount == None:
	print "\t%s comment get error" % title
	exit()

site = {}
site['title'] = title
site['url'] = movieid
site['playCount'] = playCount
site['commentCount'] = commentCount

data['sites'].insert(0, site)

# write json
file = open(jsonfile, 'w')
json.dump(data, file, indent=4)
file.close()

print '%s %s %s %s added' % (title, movieid, playCount, commentCount)
