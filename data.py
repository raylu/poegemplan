import json

import httpx

def main():
	res = httpx.get('https://poegems.com/json')
	res.raise_for_status()

	gems = {}
	for gem in res.json():
		name = gem['name']
		if name.endswith('s Mark'):
			name = name[:-len('s Mark')] + "'s Mark"
		quests = gem['quests']
		for quest in quests:
			if quest['classes'].startswith('All, Classes'):
				quest['classes'] = 'All'
			else:
				quest['classes'] = quest['classes'].split(', ')
		gems[name] = quests

	with open('gems.json', 'w') as f:
		json.dump(gems, f)

if __name__ == '__main__':
	main()