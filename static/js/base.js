const EMPTY_PFP = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxIiBoZWlnaHQ9IjEiLz4K";

const api = {
	fetch: (method, url, body) => {
		let options = {
			method: method,
			headers: {
				"Accept": "application/json",
				"Content-Type": "application/json"
			},
			body: body ? JSON.stringify(body) : null
		};
		return fetch(url, options).then((res) => {
			if (res.headers.get("content-type") != "application/json") {
				return null;
			}
			return res.json();
		});
	}
};
