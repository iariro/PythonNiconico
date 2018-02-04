#!/usr/bin/python

import json
import sys

if len(sys.argv) < 2:
	print 'Usage: jsonfile title'
	exit()

jsonfile = sys.argv[1]
print jsonfile
keyword = None
if len(sys.argv) >= 3:
	keyword = sys.argv[2]

# read json
file = open(jsonfile, 'r')
data = json.load(file)
file.close()

for site in data['sites']:
	if keyword == None or keyword in site['title']:
		title = site['title']
		comment = float(site['commentCount'])
		play = float(site['playCount'])
		print '%s %d %d %f' % (title, comment, play, (comment * 100)/play)
