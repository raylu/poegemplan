import dataclasses
import json
import re

import httpx

@dataclasses.dataclass
class Stats:
	flat_life: int
	increased_life: int
	strength: int

def analyze(account, character):
	client = httpx.Client()
	client.headers['User-Agent'] = 'Mozilla/5.0'
	params = {'accountName': account, 'character': character, 'realm': 'pc'}
	r = client.post('https://www.pathofexile.com/character-window/get-items', data=params)
	r.raise_for_status()
	character = r.json()

	r = client.get('https://www.pathofexile.com/character-window/get-passive-skills', params=params)
	r.raise_for_status()
	skills = r.json()

	tree, masteries = _passive_skill_tree(client)

	stats = Stats(flat_life=38 + character['character']['level'] * 12,
		increased_life=0,
		strength=20)
	for item in character['items']:
		for modlist in ['implicitMods', 'explicitMods', 'craftedMods']:
			if modlist not in item:
				continue
			_parse_mods(stats, item[modlist])

	for h in skills['hashes']:
		node = tree['nodes'][str(h)]
		_parse_mods(stats, node['stats'])

	cluster_jewel_nodes = {}
	for jewel in skills['jewel_data'].values():
		if 'subgraph' in jewel:
			cluster_jewel_nodes.update(jewel['subgraph']['nodes'])
	for h in skills['hashes_ex']:
		node = cluster_jewel_nodes[str(h)]
		_parse_mods(stats, node['stats'])

	for mastery_effect in skills['mastery_effects']:
		node_stats = masteries[int(mastery_effect) >> 16]
		_parse_mods(stats, node_stats)

	print(stats)
	stats.flat_life += stats.strength // 2
	print(stats)

def _passive_skill_tree(client):
	r = client.get('https://www.pathofexile.com/passive-skill-tree', headers={'User-Agent': 'Mozilla/5.0'})
	r.raise_for_status()
	tree = r.text[r.text.index('passiveSkillTreeData'):]
	tree = tree[tree.index('{'):]
	tree = tree[:tree.index('};') + 1]
	tree_dict = json.loads(tree)

	masteries = {}
	for node in tree_dict['nodes'].values():
		if 'masteryEffects' not in node:
			continue
		for effect in node['masteryEffects']:
			masteries[effect['effect']] = effect['stats']
	return tree_dict, masteries

matchers = [(re.compile(pattern), attr) for pattern, attr in [
	(r'\+(\d+) to maximum Life', 'flat_life'),
	(r'(\d+)% increased maximum Life', 'increased_life'),
	(r'\+(\d+) to (Strength.*|all Attributes)', 'strength'),
]]

def _parse_mods(stats: Stats, mods: list) -> None:
	for mod in mods:
		for regex, attr in matchers:
			m = regex.match(mod)
			if m:
				value = int(m.group(1))
				setattr(stats, attr, getattr(stats, attr) + value)

if __name__ == '__main__':
	analyze('raylu', 'rayluloop')
