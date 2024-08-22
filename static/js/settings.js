document.addEventListener("alpine:init", () => {
	Alpine.data("settings", () => ({
		info: {},
		interests: [],
		file: null,
		password: "",
		password_repeated: "",
		score: {width: "0%"},
		error: null,

		init() {
			this.$watch("password", () => this.score_update());
			this.$watch("file", () => this.pfp_update());

			const auth_handler = () => {
				if (!this.account.authenticated) {
					return;
				}

				if (this.account.is_adv) {
					this.fetch("GET", "/api/settings/adv").then((res) => {
						this.info = res.adv;
					});
				} else {
					this.fetch("GET", "/api/settings/user").then((res) => {
						this.info = res.user;
						this.interests = res.user.interests ?? [];
						this.info.pfp ??= PFP_EMPTY;
						this.info.birthday &&= new Date(new Date(this.info.birthday) + "UTC").toISOString().split("T")[0];;
					});
				}
			};
			this.$watch("account.authenticated", auth_handler);
			auth_handler();
		},

		submit() {
			if (this.password != this.password_repeated) {
				this.error = "Passwords don't match";
				return;
			}

			if (this.account.is_adv) {
				this.fetch("PUT", "/api/settings/adv", {
					display_name: this.info.name,
					industry: this.info.industry,
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
					display_name: this.info.name,
					gender: this.info.gender,
					biography: this.info.biography,
					birthday: this.info.birthday,
					password: this.password,
					interests: this.info.interests.map((tag) => tag.id)
				}));
				form.append("pfp", this.file);

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
			if (!this.pfp_.type.startsWith("image/")) {
				this.error = "Couldn't load profile picture";
				return;
			}
			this.info.pfp = URL.createObjectURL(this.file);
		}
	}));
});
