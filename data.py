import json

import httpx

def main():
	res = httpx.get('https://poegems.com/json')
	res.raise_for_status()

	input_gems = {gem['uuid']: gem for gem in res.json()}

	output_gems = {}
	for gem in input_gems.values():
		name: str = gem['name']
		if name.endswith('s Mark'):
			name = name[:-len('s Mark')] + "'s Mark"

		if base_gem := gem.get('baseGem'):
			input_quests: list[dict] = input_gems[base_gem]['quests']
		else:
			input_quests = gem['quests']
		output_quests = []
		for quest in input_quests:
			quest = quest.copy()
			if quest['classes'].startswith('All, Classes'):
				quest['classes'] = 'All'
			else:
				quest['classes'] = quest['classes'].split(', ')
			output_quests.append(quest)
		output_gems[name] = {'quests': output_quests, 'src': gem['src']}

	with open('gems.json', 'w', encoding='utf-8') as f:
		json.dump(output_gems, f)

if __name__ == '__main__':
	main()
