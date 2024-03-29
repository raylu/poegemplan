#!/usr/bin/env python3

import sys
if len(sys.argv) == 3:
	import eventlet
	import eventlet.wsgi
	eventlet.monkey_patch()

# pylint: disable=wrong-import-position
import base64
import mimetypes
import json
import xml.etree.ElementTree
import zlib

import httpx
from pigwig import PigWig, Response

def root(request, short=None):
	with open('index.html', 'rb') as f:
		return Response(f.read(), content_type='text/html; charset=UTF-8')

def static(request, path):
	content_type, _ = mimetypes.guess_type(path)
	with open('static/' + path, 'rb') as f:
		return Response(f.read(), content_type=content_type)

def quests(request):
	return Response.json(quest_names)

def pob(request, short):
	res = httpx.get('https://poe.ninja/pob/raw/' + short)
	res.raise_for_status()
	pob_xml = zlib.decompress(base64.urlsafe_b64decode(res.text))
	xml_root = xml.etree.ElementTree.fromstring(pob_xml)

	class_name = xml_root.find('Build').get('className')

	build_gems = []
	for skill in xml_root.find('Skills').iter('Skill'):
		if skill.get('source'):
			continue
		enabled = skill.get('enabled') == 'true'
		for gem in skill.iter('Gem'):
			name = gem.get('nameSpec')
			try:
				if gem.get('skillId').startswith('Vaal'):
					gem_quests = gems[name[len('Vaal '):]]['quests']
					src = gems[name]['src']
				else:
					data_name = name
					if gem.get('skillId').startswith('Support'):
						data_name += ' Support'
					if data_name.startswith('Awakened '):
						gem_quests = gems[data_name[len('Awakened '):]]['quests']
					else:
						gem_quests = gems[data_name]['quests']
					src = gems[data_name]['src']
			except KeyError:
				continue
			build_gems.append({
				'name': name,
				'enabled': enabled and gem.get('enabled') == 'true',
				'quests': gem_quests,
				'src': src,
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
gems = None
quest_names = [
	'the_twilight_strand',
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
]

def main():
	global gems
	with open('gems.json', 'r', encoding='utf-8') as f:
		gems = json.load(f)
	if len(sys.argv) == 3:
		addr = sys.argv[1]
		port = int(sys.argv[2])
		eventlet.wsgi.server(eventlet.listen((addr, port)), app)
	else:
		app.main()

if __name__ == '__main__':
	main()
