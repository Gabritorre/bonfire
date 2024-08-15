const EMPTY_PFP = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxIiBoZWlnaHQ9IjEiLz4K";

document.addEventListener("alpine:init", () => {
	Alpine.data("base", () => ({
		account: Alpine.$persist({
			authenticated: null,
			id: null,
			handle: null,
			name: null,
			pfp: EMPTY_PFP,
			is_adv: false
		}),
		popup: {
			title: null,
			body: null,
			modal: null,
			confirmed: false,
			resolve: null
		},

		init() {
			this.popup.modal = new bootstrap.Modal(this.$refs.popup);
			this.$refs.popup.addEventListener("hidden.bs.modal", () => {
				this.popup.resolve(this.popup.confirmed);
			});

			this.fetch("GET", "/api/profile").then((res) => {
				this.account.authenticated = res.error == null;
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
				this.account.handle = res.user.handle;
				this.account.name = res.user.name;
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
		},

		alert(title, body) {
			this.popup.title = title;
			this.popup.body = body;
			this.popup.confirmed = false;
			this.popup.modal.show();
			return new Promise((resolve, reject) => {
				this.popup.resolve = resolve;
			});
		}
	}));
});
