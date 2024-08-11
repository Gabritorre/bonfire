document.addEventListener("alpine:init", () => {
	Alpine.data("header", () => ({
		id: null,
		pfp: EMPTY_PFP,
		is_adv: false,
		logged: null,

		init() {
			api.fetch("GET", "/api/profile").then((res) => {
				this.logged = res.error == null;
				if (res.error) {
					return;
				}

				this.id = res.id;
				this.is_adv = res.is_adv ?? this.is_adv;
				if (this.is_adv) {
					return null;
				}
				return api.fetch("POST", "/api/profile/user", {id: res.id});
			}).then((res) => {
				if (!res || res.error) {
					return;
				}
				this.pfp = res.user.pfp ?? this.pfp;
			});
		},

		logout() {
			api.fetch("GET", "/api/profile/logout").then((_) => {
				window.location.href = "/";
			});
		}
	}));
});
