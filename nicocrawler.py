#!/usr/local/bin/python3

import urllib.request
from bs4 import BeautifulSoup
import datetime
import json
import re
import sys
import time
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

if len(sys.argv) < 2:
	print('Usage: jsonfile')
	exit()

for jsonfile in sys.argv[1:]:
	print(jsonfile)

	# read json
	file = open(jsonfile, 'r')
	data = json.load(file)
	file.close()

	# update datetime
	pupdatetime = "-"
	updatetime = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
	if 'datetime' in data:
		pupdatetime = data['datetime']
	print('%s -> %s' % (pupdatetime, updatetime))
	data['datetime'] = updatetime 

	userComments1 = r'.*viewCount&quot;:([0-9]*),.*commentCount&quot;:([0-9]*).*'
	userComments2 = r'([0-9]*) UserPlays, ([0-9]*) UserComments'

	for site in data['sites']:
		time.sleep(0)

		# get HTML
		url = 'http://www.nicovideo.jp/watch/%s' % site['url']
		html = urllib.request.urlopen(url)
		soup = BeautifulSoup(html, "html.parser")

		# get UserComments count
		playCount = None
		commentCount = None
		metas = soup.find_all('meta', attrs={'itemprop':'interactionCount'})
		for meta in metas:
			match = re.search(userComments2, meta.get('content'))
			if match != None:
				playCount = int(match.group(1))
				commentCount = int(match.group(2))

		#print(site['title'], playCount, commentCount)

		if commentCount == None:
			metas = soup.find_all('script', attrs={'type':'application/ld+json'})
			for meta in metas:
				try:
					js = json.loads(meta.string)
					if 'interactionCount' in js and 'commentCount' in js:
						playCount = js['interactionCount']
						commentCount = js['commentCount']
				except json.decoder.JSONDecodeError:
					pass

		if commentCount == None:
			elements = soup.find_all('span')
			class_name1 = None
			class_name2 = None
			for element in elements:
				if element.has_attr('class'):
					class_name1 = element['class']
					if 'FormattedNumber' in class_name1:
						if 'VideoViewCountMeta-counter' in class_name2:
							playCount = int(element.string.replace(',', ''))
						elif 'CommentCountMeta-counter' in class_name2:
							commentCount = int(element.string.replace(',', ''))
					else:
						if 'VideoViewCountMeta-counter' in class_name1:
							class_name2 = class_name1
						elif 'CommentCountMeta-counter' in class_name1:
							class_name2 = class_name1
# <span class="VideoViewCountMeta-counter"><span class="FormattedNumber">54,741</span></span>
# <span class="FormattedNumber">54,741</span>
# <span class="CommentCountMeta-counter"><span class="FormattedNumber">1,254</span></span>

		# update count
		if commentCount == None:
			print("\t%s comment get error" % site['title'])

			file2 = open('dump.html', 'w')
			file2.write(str(soup))
			file2.close()

			break
			continue

		if 'playCount' in site == False:
			site['playCount'] = 0
		if 'commentCount' in site == False:
			site['commentCount'] = 0
		if commentCount > int(site['commentCount']):
			print("\t%s %s->%s" % (site['title'], site['commentCount'], commentCount))
		site['playCount'] = playCount
		site['commentCount'] = commentCount

	# write json
	file = open(jsonfile, 'w')
	json.dump(data, file, indent=4)
	file.close()
