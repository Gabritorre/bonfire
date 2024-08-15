const PFP_EMPTY = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxIiBoZWlnaHQ9IjEiLz4K";

const PASSWORD_ENTROPY_RANGES = [
	{range: [0, 25], color: "--bs-red", width: 25},
	{range: [25, 50], color: "--bs-orange", width: 50},
	{range: [50, 75], color: "--bs-yellow", width: 75},
	{range: [75, Infinity], color: "--bs-green", width: 100}
];

document.addEventListener("alpine:init", () => {
	Alpine.data("base", () => ({
		account: Alpine.$persist({
			authenticated: null,
			id: null,
			handle: null,
			name: null,
			pfp: PFP_EMPTY,
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
				this.account.authenticated = null;
				this.account.pfp = PFP_EMPTY;
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
		},

		suffixize(number) {
			const suffixes = ["", "K", "M", "B", "T"];
			let i = Math.min(Math.floor(Math.log10(number)/3), suffixes.length-1);
			let scaled = number / 10**(i*3);
			let rounded = Math.round(scaled*10)/10;
			return rounded + suffixes[i];
		},

		entropy(password) {
			let codes = Array.from(password ?? "").map((c) => c.charCodeAt(0));
			let range = Math.max(...codes) - Math.min(...codes) + 1;
			let entropy = password?.length * Math.log2(range) || 0;
			let item = PASSWORD_ENTROPY_RANGES.filter((item) => item.range[0] <= entropy && entropy <= item.range[1])[0];
			let color = "var(" + item.color + ")";
			let width = item.width + "%";
			return [color, width];
		}
	}));
});
