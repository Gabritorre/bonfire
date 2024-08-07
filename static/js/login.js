const login = {
	submit: (ctx) => {
		api.fetch("POST", "/api/profile/login", {
			handle: ctx.handle,
			password: ctx.password
		}).then((res) => {
			if (!res.error) {
				window.location.pathname = "/settings";
				return;
			}
			ctx.error = true;
		})
	}
};
