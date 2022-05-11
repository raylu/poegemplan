'use strict';
(() => {
	const questsPromise = fetch('/quests');
	let quests = null;

	document.querySelector('form#pob').addEventListener('submit', async (event) => {
		event.preventDefault();
		const short = document.querySelector('form#pob input[name="short"]').value;
		load(short);
		history.pushState({}, '', '/pob/' + short);
	});

	if (window.location.pathname.substr(0, 5) === '/pob/') {
		load(window.location.pathname.substr(5));
	}

	async function load(short) {
		const pobRes = await fetch('/pob/raw/' + short);
		const build = await pobRes.json();

		if (quests === null) {
			const questsRes = await questsPromise;
			quests = await questsRes.json();
		}
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
			for (const quest of gem['quests']) {
				if (quest['classes'] === 'All' || quest['classes'].indexOf(build['class']) !== -1) {
					const gemDiv = document.createElement('div');
					gemDiv.classList.add('gem');
					const img = document.createElement('img');
					img.src = 'https://web.poecdn.com/gen/image/' + gem['src'];
					const name = document.createElement('div');
					name.innerText = gem['name'];
					gemDiv.appendChild(img);
					gemDiv.appendChild(name);
					main.querySelector('#' + quest['name']).appendChild(gemDiv);
					break;
				}
			}
		}
	}

	function formatQuest(quest) {
		quest = quest.replaceAll('_s_', "'s ");
		quest = quest.replaceAll('_', ' ');
		const split = quest.split(' ');
		const first = split[0].charAt(0).toUpperCase() + split[0].substr(1);
		const rest = split.splice(1).map(function(word) {
			if (['and', 'at', 'in', 'of', 'the'].indexOf(word) !== -1)
				return word;
			return (word.charAt(0).toUpperCase() + word.substr(1));
		}).join(' ');
		return `${first} ${rest}`;
	}
})();
