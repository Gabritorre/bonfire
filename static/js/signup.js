const ENTROPY_RANGES = [
	{range: [0, 25], color: "--bs-red", width: 25},
	{range: [25, 50], color: "--bs-orange", width: 50},
	{range: [50, 75], color: "--bs-yellow", width: 75},
	{range: [75, Infinity], color: "--bs-green", width: 100}
];

document.addEventListener("alpine:init", () => {
	Alpine.data("signup", () => ({
		handle: "",
		password: "",
		password_repeated: "",
		score: {},
		is_adv: false,
		error: "",

		init() {
			this.$watch("password", () => this.update_score());
		},

		update_score() {
			let repeat = this.$refs.repeat;
			let is_collapsed = repeat.classList.contains("collapse") && !repeat.classList.contains("show");
			if ((this.password.length > 0 && is_collapsed) || (this.password.length == 0 && !is_collapsed)) {
				new bootstrap.Collapse(repeat);
			}

			let codes = Array.from(this.password).map((c) => c.charCodeAt(0));
			let range = Math.max(...codes) - Math.min(...codes) + 1;
			let entropy = this.password.length * Math.log2(range) || 0;
			let item = ENTROPY_RANGES.filter((item) => item.range[0] <= entropy && entropy <= item.range[1])[0];
			this.score["background-color"] = "var(" + item.color + ")";
			this.score["width"] = item.width + "%";
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
				if (!res.error) {
					window.location.pathname = "/settings";
					return;
				}
				this.error = res.error;
			})
		}
	}));
});
