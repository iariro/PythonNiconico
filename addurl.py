#!/usr/bin/python

import datetime
import json
import re
import subprocess
import sys

if len(sys.argv) < 4:
	print 'Usage: jsonfile title url'
	exit()

(jsonfile,title,url) = sys.argv[1:4]
movieid = re.sub('http://www.nicovideo.jp/watch/', '', url)

# read json
file = open(jsonfile, 'r')
data = json.load(file)
file.close()

# userComments = r'.*"([0-9]*) UserPlays, ([0-9]*) UserComments".*'
userComments = r'.*viewCount&quot;:([0-9]*),.*commentCount&quot;:([0-9]*).*'

# get HTML
url = 'http://www.nicovideo.jp/watch/%s' % movieid
curlCommand = [ 'curl', '-s',  url]
res = subprocess.check_output(curlCommand)

# get UserComments count
playCount = None
commentCount = None
lines = res.split('\n')
for line in lines:
	if re.match(userComments, line):
		playCount = re.sub(userComments, r'\1', line)
		commentCount = re.sub(userComments, r'\2', line)
		break

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
