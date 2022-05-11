'use strict';
(() => {
	const questsPromise = fetch('/quests');
	let quests = null;

	document.querySelector('form#pob').addEventListener('submit', async (event) => {
		event.preventDefault();
		const short = document.querySelector('form#pob input[name="short"]').value;
		load(short);
		history.pushState({}, '', 'pob/' + short);
	});

	if (window.location.pathname.substr(0, 5) === '/pob/') {
		load(window.location.pathname.substr(5));
	}

	async function load(short) {
		const pobRes = await fetch('/pob/raw/' + short);
		const code = await pobRes.json();
		console.log(code);

		if (quests === null) {
			const questsRes = await questsPromise;
			quests = await questsRes.json();
		}

		const main = document.querySelector('main');
		for (const quest of quests) {
			const section = document.createElement('section');
			section.innerText = quest;
			main.appendChild(section);
		}
	}
})();
