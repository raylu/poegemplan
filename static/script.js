'use strict';
(() => {
	const questsPromise = fetchQuests();

	const shortInput = document.querySelector('form#pob input[name="short"]');
	document.querySelector('form#pob').addEventListener('submit', (event) => {
		event.preventDefault();
		const short = shortInput.value;
		load(short);
		history.pushState({}, '', '/pob/' + short);
	});

	if (window.location.pathname.substr(0, 5) === '/pob/') {
		const short = window.location.pathname.substr(5);
		shortInput.value = short;
		load(short);
	}

	async function fetchQuests() {
		const res = await fetch('/quests');
		return res.json();
	}

	async function load(short) {
		const pobRes = await fetch('/pob/raw/' + short);
		const build = await pobRes.json();
		const quests = await questsPromise;
		quests.push('unpurchasable');

		const main = document.querySelector('main');
		main.innerHTML = '';
		for (const quest of quests) {
			const section = document.createElement('section');
			section.id = quest;
			const div = document.createElement('div');
			div.classList.add('quest_name');
			div.innerText = formatQuest(quest);
			section.appendChild(div);
			main.appendChild(section);
		}

		for (const gem of build['gems']) {
			let purchasable = false;
			for (const quest of gem['quests']) {
				if (quest['classes'] === 'All' || quest['classes'].indexOf(build['class']) !== -1) {
					const gemDiv = renderGem(gem);
					main.querySelector('#' + quest['name']).appendChild(gemDiv);
					purchasable = true;
					break;
				}
			}
			if (!purchasable) {
				const gemDiv = renderGem(gem);
				main.querySelector('#unpurchasable').appendChild(gemDiv);
			}
		}
	}

	function renderGem(gem) {
		const gemDiv = document.createElement('div');
		gemDiv.classList.add('gem');
		if (!gem['enabled'])
			gemDiv.classList.add('disabled');
		const img = document.createElement('img');
		img.src = 'https://web.poecdn.com/gen/image/' + gem['src'];
		const name = document.createElement('div');
		name.innerText = gem['name'];
		gemDiv.appendChild(img);
		gemDiv.appendChild(name);
		return gemDiv;
	}

	function formatQuest(quest) {
		const split = quest.replaceAll('_s_', '\'s_').split('_');
		const first = split[0].charAt(0).toUpperCase() + split[0].substr(1);
		const rest = split.splice(1).map((word) => {
			if (['and', 'at', 'in', 'of', 'the'].indexOf(word) !== -1)
				return word;
			return word.charAt(0).toUpperCase() + word.substr(1);
		}).join(' ');
		return `${first} ${rest}`;
	}
})();
