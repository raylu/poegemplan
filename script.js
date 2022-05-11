'use strict';
(() => {
	const questsPromise = fetch('/quests');
	let quests = null;

	document.querySelector('form#pob').addEventListener('submit', async (event) => {
		event.preventDefault();
		const pobRes = await fetch('/pob/6HZ');
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
	});
})();
