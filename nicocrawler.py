#!/usr/bin/python

import datetime
import json
import re
import subprocess
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
	userComments2 = r'.*"([0-9]*) UserPlays, ([0-9]*) UserComments".*'

	for site in data['sites']:
		time.sleep(0)

		# get HTML
		url = 'http://www.nicovideo.jp/watch/%s' % site['url']
		curlCommand = [ 'curl', '-s',  url]
		res = subprocess.check_output(curlCommand)

		# get UserComments count
		playCount = None
		commentCount = None
		lines = res.split('\n')
		for line in lines:
			if re.match(userComments1, line):
				playCount = re.sub(userComments1, r'\1', line)
				commentCount = re.sub(userComments1, r'\2', line)
				break
			elif re.match(userComments2, line):
				playCount = re.sub(userComments2, r'\1', line)
				commentCount = re.sub(userComments2, r'\2', line)
				break

		print site['title'], playCount, commentCount

		# update count
		if commentCount == None:
			print "\t%s comment get error" % site['title']

			file2 = open('dump.html', 'w')
			file2.write(res)
			file2.close()

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
