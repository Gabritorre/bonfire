document.addEventListener("alpine:init", () => {
	Alpine.data("login", () => ({
		handle: "",
		password: "",
		error: "",

		submit() {
			api.fetch("POST", "/api/profile/login", {
				handle: this.handle,
				password: this.password
			}).then((res) => {
				if (!res.error) {
					window.location.pathname = "/";
					return;
				}
				this.error = res.error;
			});
		}
	}));
});
