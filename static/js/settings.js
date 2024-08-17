document.addEventListener("alpine:init", () => {
	Alpine.data("settings", () => ({
		handle: null,
		name: null,
		industry: null,
		gender: null,
		pfp: PFP_EMPTY,
		pfp_file: null,
		birthday: null,
		biography: null,
		password: "",
		password_repeated: "",
		score: {width: "0%"},
		interests: [],
		error: null,

		init() {
			this.$watch("password", () => this.score_update());
			this.$watch("pfp_file", () => this.pfp_update());

			if (this.account.is_adv) {
				this.fetch("GET", "/api/settings/adv").then((res) => {
					this.handle = res.adv.handle;
					this.name = res.adv.name;
					this.industry = res.adv.industry;
				});
			} else {
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
			}
		},

		submit() {
			if (this.password != this.password_repeated) {
				this.error = "Passwords don't match";
				return;
			}

			if (this.account.is_adv) {
				this.fetch("PUT", "/api/settings/adv", {
					display_name: this.name,
					industry: this.industry,
					password: this.password
				}).then((res) => {
					if (!res.error) {
						window.location.reload();
						return;
					}
					this.error = res.error;
				});
			} else {
				let form = new FormData();
				form.append("json", JSON.stringify({
					display_name: this.name,
					gender: this.gender,
					biography: this.biography,
					birthday: this.birthday,
					password: this.password,
					interests: this.interests.map((tag) => tag.id)
				}));
				form.append("pfp", this.pfp_file);

				this.fetch("PUT", "/api/settings/user", form).then((res) => {
					if (!res.error) {
						window.location.reload();
						return;
					}
					this.error = res.error;
				});
			}
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

		score_update() {
			let [color, width] = this.entropy(this.password);
			this.score["background-color"] = color;
			this.score["width"] = width;
		},

		pfp_update() {
			if (!this.pfp_file.type.startsWith("image/")) {
				this.error = "Couldn't load profile picture";
				return;
			}
			this.pfp = URL.createObjectURL(this.pfp_file);
		}
	}));
});
