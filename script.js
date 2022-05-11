'use strict';
(() => {
	document.querySelector('form#pob').addEventListener('submit', async (event) => {
		event.preventDefault();
		const res = await fetch('/pob/6HZ');
		const code = await res.json();
		console.log(code);
	});
})();
