document.addEventListener("alpine:init", () => {
	Alpine.data("login", () => ({
		handle: "",
		password: "",
		error: "",

		submit() {
			this.fetch("POST", "/api/profile/login", {
				handle: this.handle,
				password: this.password
			}).then((res) => {
				if (res.error) {
					this.error = res.error;
					return;
				}
				this.account.authenticated = null;
				window.location.pathname = "/";
			});
		}
	}));
});
