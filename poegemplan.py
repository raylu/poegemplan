#!/usr/bin/env python3

import sys
if len(sys.argv) == 2:
	import eventlet
	import eventlet.wsgi
	eventlet.monkey_patch()

import base64
import mimetypes
import json
import xml.etree.ElementTree
import zlib

import httpx
from pigwig import PigWig, Response

def root(request, short=None):
	with open('index.html', 'r') as f:
		return Response(f.read(), content_type='text/html; charset=UTF-8')

def static(request, path):
	content_type, _ = mimetypes.guess_type(path)
	with open('static/' + path, 'r') as f:
		return Response(f.read(), content_type=content_type)

def style(request):
	with open('style.css', 'r') as f:
		return Response(f.read(), content_type='text/css')

def quests(request):
	return Response.json(quests)

def pob(request, short):
	res = httpx.get('https://poe.ninja/pob/raw/' + short)
	res.raise_for_status()
	pob_xml = zlib.decompress(base64.urlsafe_b64decode(res.text))
	root = xml.etree.ElementTree.fromstring(pob_xml)

	class_name = root.find('Build').get('className')

	build_gems = []
	for skill in root.find('Skills').iter('Skill'):
		if skill.get('enabled') == 'false' or skill.get('source'):
			continue
		for gem in skill.iter('Gem'):
			if gem.get('enabled') == 'false':
				continue
			name = gem.get('nameSpec')
			if gem.get('skillId').startswith('Support'):
				name += ' Support'
			try:
				gem_data = gems[name]
			except KeyError:
				continue
			build_gems.append({
				'name': name,
				'quests': gem_data['quests'],
				'src': gem_data['src'],
			})
	return Response.json({'class': class_name, 'gems': build_gems})

routes = [
	('GET', '/', root),
	('GET', '/pob/<short>', root),
	('GET', '/static/<path:path>', static),
	('GET', '/quests', quests),
	('GET', '/pob/raw/<short>', pob),
]

app = PigWig(routes)

quests = [
	'enemy_at_the_gate',
	'mercy_mission',
	'breaking_some_eggs',
	'the_caged_brute',
	'the_siren_s_cadence',
	'intruders_in_black',
	'sharp_and_cruel',
	'the_root_of_the_problem',
	'lost_in_love',
	'sever_the_right_hand',
	'a_fixture_of_fate',
	'breaking_the_seal',
	'the_eternal_nightmare',
	'the_twilight_strand',
]

if __name__ == '__main__':
	with open('gems.json', 'r') as f:
		gems = json.load(f)
	if len(sys.argv) == 2:
		port = int(sys.argv[1])
		eventlet.wsgi.server(eventlet.listen(('127.0.0.1', port)), app)
	else:
		app.main()
