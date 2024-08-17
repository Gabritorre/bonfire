document.addEventListener("alpine:init", () => {
	Alpine.data("settings", () => ({
		handle: null,
		name: null,
		gender: null,
		pfp: PFP_EMPTY,
		birthday: null,
		biography: null,
		password: "",
		password_repeated: "",
		score: {width: "0%"},
		interests: [],
		error: null,

		init() {
			this.$watch("password", () => this.score_update());

			this.fetch("GET", "/api/settings/user").then((res) => {
				this.handle = res.user.handle;
				this.name = res.user.name;
				this.biography = res.user.biography;
				this.gender = res.user.gender ?? this.gender;
				this.pfp = res.user.pfp ?? PFP_EMPTY;
				this.interests = res.user.interests ?? [];
				if (res.user.birthday) {
					this.birthday = new Date(new Date(res.user.birthday) + "UTC").toISOString().split("T")[0];
				}
			});
		},

		submit() {
			if (this.password != this.password_repeated) {
				this.error = "Passwords don't match";
				return;
			}

			this.fetch("PUT", "/api/settings/user", {
				display_name: this.name,
				gender: this.gender,
				biography: this.biography,
				birthday: this.birthday,
				password: this.password,
				interests: this.interests.map((tag) => tag.id)
			}).then((res) => {
				if (!res.error) {
					window.location.reload();
					return;
				}
				this.error = res.error;
			});
		},

		score_update() {
			let [color, width] = this.entropy(this.password);
			this.score["background-color"] = color;
			this.score["width"] = width;
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
