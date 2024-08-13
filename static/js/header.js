document.addEventListener("alpine:init", () => {
	Alpine.data("header", () => ({
		authenticated: null,
		account: {
			id: null,
			handle: null,
			name: null,
			pfp: EMPTY_PFP,
			is_adv: false
		},

		init() {
			api.fetch("GET", "/api/profile").then((res) => {
				this.authenticated = res.error == null;
				if (res.error) {
					return;
				}

				this.account.id = res.id;
				this.account.is_adv = res.is_adv;
				if (this.account.is_adv) {
					return null;
				}
				return api.fetch("POST", "/api/profile/user", {id: this.account.id});
			}).then((res) => {
				if (!res || res.error) {
					return;
				}
				this.account.pfp = res.user.pfp ?? this.account.pfp;
				this.account.handle = res.user.username;
				this.account.name = res.user.display_name;
			});
		},

		logout() {
			api.fetch("GET", "/api/profile/logout").then((_) => {
				window.location.href = "/";
			});
		}
	}));
});
