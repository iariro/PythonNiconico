#!/usr/bin/python

import datetime
import json
import re
import subprocess

# read json
file = open('nicocrawler.json', 'r')
data = json.load(file)
file.close()

# update datetime
pdatetime = "-"
datetime = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
if data.has_key('datetime'):
	pdatetime = data['datetime']
print '%s -> %s' % (pdatetime, datetime)
data['datetime'] = datetime 

userComments = r'.* ([0-9]*) UserComments.*'

for site in data['sites']:
	# get HTML
	url = 'http://www.nicovideo.jp/watch/%s' % site['url']
	curlCommand = [ 'curl', '-s',  url]
	res = subprocess.check_output(curlCommand)

	# get UserComments count
	lines = res.split('\n')
	for line in lines:
		if re.match(userComments, line):
			commentCount = re.sub(userComments, r'\1', line)
			break

	# update count
	if site.has_key('commentCount') == False:
		site['commentCount'] = 0
	if commentCount != site['commentCount']:
		print "%s %s->%s" % (site['title'], site['commentCount'], commentCount)
	site['commentCount'] = commentCount

# write json
file = open('nicocrawler.json', 'w')
json.dump(data, file, indent=4)
file.close()
