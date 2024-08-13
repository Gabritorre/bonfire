const EMPTY_PFP = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxIiBoZWlnaHQ9IjEiLz4K";

document.addEventListener("alpine:init", () => {
	Alpine.data("base", () => ({
		authenticated: null,
		account: {
			id: null,
			handle: null,
			name: null,
			pfp: EMPTY_PFP,
			is_adv: false
		},

		init() {
			this.fetch("GET", "/api/profile").then((res) => {
				this.authenticated = res.error == null;
				if (res.error) {
					return;
				}

				this.account.id = res.id;
				this.account.is_adv = res.is_adv;
				if (this.account.is_adv) {
					return null;
				}
				return this.fetch("POST", "/api/profile/user", {id: this.account.id});
			}).then((res) => {
				if (!res || res.error) {
					return;
				}
				this.account.pfp = res.user.pfp ?? this.account.pfp;
				this.account.handle = res.user.username;
				this.account.name = res.user.display_name;
			});
		},

		fetch(method, url, body) {
			let options = {
				method: method,
				headers: {
					"Accept": "application/json",
				},
				body: body
			};

			if (body?.constructor?.name === "Object") {
				options.headers["Content-Type"] = "application/json";
				options.body = JSON.stringify(body);
			}

			return fetch(url, options).then((res) => {
				if (res.headers.get("content-type") != "application/json") {
					return null;
				}
				return res.json();
			});
		},

		logout() {
			this.fetch("GET", "/api/profile/logout").then((_) => {
				window.location.href = "/";
			});
		}
	}));
});
