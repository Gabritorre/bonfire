document.addEventListener("alpine:init", () => {
	Alpine.data("follows", () => ({
		type: null,
		users: [],

		init() {
			const params = new URLSearchParams(window.location.search);
			const id = +params.get("id");
			const type = params.get("type") ?? "s";

			const api = type === "s" ? "followers" : "followed";
			this.fetch("POST", "/api/profile/user/" + api, {id}).then((res) => {
				this.type = type;
				if (res.error) {
					return;
				}
				this.users = res[api];
			});
		}
	}));
});
