document.addEventListener("alpine:init", () => {
	Alpine.data("settings", () => ({
		handle: null,
		name: null,
		gender: null,
		pfp: EMPTY_PFP,
		birthday: null,
		biography: null,
		password: null,
		tags: [],
		error: null,

		init() {
			this.fetch("GET", "/api/settings/user").then((res) => {
				const user = res.user;
				this.handle = user.username;
				this.name = user.display_name;
				this.biography = user.biography;
				this.gender = user.gender ?? this.gender;
				this.pfp = user.pfp ?? this.pfp;
				if (user.birthday) {
					this.birthday = new Date(new Date(user.birthday) + "UTC").toISOString().split("T")[0];
				}
			});
		},

		submit() {
			this.fetch("PUT", "/api/settings/user", {
				display_name: this.name,
				gender: this.gender,
				biography: this.biography,
				birthday: this.birthday,
				password: this.password,	// TODO
				interests: this.tags
			}).then((res) => {
				if (!res.error) {
					window.location.reload();
					return;
				}
				this.error = res.error;
			});
		},

		nuke() {
			this.alert("Delete account", "Are you sure you want to delete your account?").then((confirmed) => {
				if (!confirmed) {
					return;
				}

				this.fetch("DELETE", "/api/profile").then((res) => {
					window.location.pathname = "/";
				});
			});
		},
	}));
});
