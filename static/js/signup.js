document.addEventListener("alpine:init", () => {
	Alpine.data("signup", () => ({
		handle: null,
		password: "",
		password_repeated: "",
		score: {width: "0%"},
		is_adv: false,
		error: null,

		init() {
			this.$watch("password", () => this.score_update());
		},

		score_update() {
			let repeat = this.$refs.repeat;
			let is_collapsed = repeat.classList.contains("collapse") && !repeat.classList.contains("show");
			if ((this.password.length > 0 && is_collapsed) || (this.password.length == 0 && !is_collapsed)) {
				new bootstrap.Collapse(repeat);
			}

			let [color, width] = this.entropy(this.password);
			this.score["background-color"] = color;
			this.score["width"] = width;
		},

		submit() {
			if (this.password !== this.password_repeated) {
				this.error = "Passwords don't match";
				return;
			}

			this.fetch("PUT", "/api/profile/signup", {
				handle: this.handle,
				password: this.password,
				is_adv: this.is_adv
			}).then((res) => {
				if (res.error) {
					this.error = res.error;
					return;
				}

				this.account.authenticated = null;
				window.location.pathname = this.is_adv ? "/" : "/settings";
			});
		}
	}));
});
