#!/usr/bin/env python3

import base64
import json
import xml.etree.ElementTree
import zlib

import httpx
from pigwig import PigWig, Response

def root(request):
	with open('index.html', 'r') as f:
		return Response(f.read(), content_type='text/html')

def script(request):
	with open('script.js', 'r') as f:
		return Response(f.read(), content_type='text/javascript')

def pob(request, short):
	res = httpx.get('https://poe.ninja/pob/raw/' + short)
	res.raise_for_status()
	pob_xml = zlib.decompress(base64.urlsafe_b64decode(res.text))
	root = xml.etree.ElementTree.fromstring(pob_xml)
	build_gems = []
	for skill in root.find('Skills').iter('Skill'):
		for gem in skill.iter('Gem'):
			name = gem.get('nameSpec')
			if gem.get('skillId').startswith('Support'):
				name += ' Support'
			try:
				build_gems.append({
					'name': name,
					'quests': gems[name],
				})
			except KeyError:
				continue
	return Response.json(build_gems)

routes = [
	('GET', '/', root),
	('GET', '/script.js', script),
	('GET', '/pob/<short>', pob),
]

app = PigWig(routes)
gems = {}

def main():
	with open('poegems.json', 'r') as f:
		raw_gems = json.load(f)
		for gem in raw_gems:
			name = gem['name']
			if name.endswith('s Mark'):
				name = name[:-len('s Mark')] + "'s Mark"
			gems[name] = gem['quests']

	app.main()

if __name__ == '__main__':
	main()
