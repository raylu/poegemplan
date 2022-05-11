#!/usr/bin/env python3

import base64
import json
import xml.etree.ElementTree
import zlib

import httpx
from pigwig import PigWig, Response

def root(request, short=None):
	with open('index.html', 'r') as f:
		return Response(f.read(), content_type='text/html; charset=UTF-8')

def script(request):
	with open('script.js', 'r') as f:
		return Response(f.read(), content_type='text/javascript')

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
		for gem in skill.iter('Gem'):
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
	('GET', '/script.js', script),
	('GET', '/style.css', style),
	('GET', '/quests', quests),
	('GET', '/pob/raw/<short>', pob),
]

app = PigWig(routes)

quests = [
	'enemy_at_the_gate',
	'the_caged_brute',
	'the_siren_s_cadence',
	'breaking_some_eggs',
	'mercy_mission',
	'sharp_and_cruel',
	'intruders_in_black',
	'the_root_of_the_problem',
	'lost_in_love',
	'sever_the_right_hand',
	'a_fixture_of_fate',
	'the_eternal_nightmare',
	'breaking_the_seal',
	'the_twilight_strand',
]

if __name__ == '__main__':
	with open('gems.json', 'r') as f:
		gems = json.load(f)
	app.main()
