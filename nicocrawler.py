#!/usr/bin/python

import urllib
from bs4 import BeautifulSoup
import datetime
import json
import re
import sys
import time

if len(sys.argv) < 2:
	print 'Usage: jsonfile'
	exit()

for jsonfile in sys.argv[1:]:
	print jsonfile

	# read json
	file = open(jsonfile, 'r')
	data = json.load(file)
	file.close()

	# update datetime
	pupdatetime = "-"
	updatetime = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
	if data.has_key('datetime'):
		pupdatetime = data['datetime']
	print '%s -> %s' % (pupdatetime, updatetime)
	data['datetime'] = updatetime 

	userComments1 = r'.*viewCount&quot;:([0-9]*),.*commentCount&quot;:([0-9]*).*'
	userComments2 = r'([0-9]*) UserPlays, ([0-9]*) UserComments'

	for site in data['sites']:
		time.sleep(0)

		# get HTML
		url = 'http://www.nicovideo.jp/watch/%s' % site['url']
		html = urllib.urlopen(url)
		soup = BeautifulSoup(html, "html.parser")

		# get UserComments count
		playCount = None
		commentCount = None
		metas = soup.find_all('meta', attrs={'itemprop':'interactionCount'})
		for meta in metas:
			match = re.search(userComments2, meta.get('content'))
			if match != None:
				playCount = match.group(1)
				commentCount = match.group(2)

		#print site['title'], playCount, commentCount

		# update count
		if commentCount == None:
			print "\t%s comment get error" % site['title']

			file2 = open('dump.html', 'w')
			file2.write(str(html))
			file2.close()

			break
			continue

		if site.has_key('playCount') == False:
			site['playCount'] = 0
		if site.has_key('commentCount') == False:
			site['commentCount'] = 0
		if commentCount != site['commentCount']:
			print "\t%s %s->%s" % (site['title'], site['commentCount'], commentCount)
		site['playCount'] = playCount
		site['commentCount'] = commentCount

	# write json
	file = open(jsonfile, 'w')
	json.dump(data, file, indent=4)
	file.close()
