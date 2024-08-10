const api = {
	fetch: (method, url, body) => {
		let options = {
			method: method,
			headers: {
				"Accept": "application/json",
				"Content-Type": "application/json"
			}
		};
		if (body) {
			options.body = JSON.stringify(body);
		}
		return fetch(url, options).then((response) => response.json());
	}
};
