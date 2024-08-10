const DELETE_WARNINGS = ["Delete account", "Are you sure?", "Are you <strong>really</strong> sure?"];

document.addEventListener("alpine:init", () => {
	Alpine.data("settings", () => ({
		handle: "",
		name: "",
		gender: "",
		pfp: "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxIiBoZWlnaHQ9IjEiLz4K",
		birthday: "",
		biography: "",
		warn: DELETE_WARNINGS[0],

		init() {
			api.fetch("GET", "/api/settings/user").then((res) => {
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

		nuke() {
			let i = DELETE_WARNINGS.indexOf(this.warn)+1;
			if (i >= DELETE_WARNINGS.length) {
				api.fetch("DELETE", "/api/profile").then((res) => {
					window.location.pathname = "/";
				});
			} else {
				this.warn = DELETE_WARNINGS[i];
			}
		},

		submit() {
			// TODO
		},
	}));
});
