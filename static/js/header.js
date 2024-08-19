document.addEventListener("alpine:init", () => {
	Alpine.data("header", () => ({
		search: null,
		query: null,
		results: [],
		error: null,

		init() {
			this.search = new bootstrap.Dropdown(this.$refs.search);
			window.a = this;
			this.$watch("query", () => this.search_update());
		},

		search_update() {
			if (!this.query) {
				this.results = [];
				this.search.hide();
				return;
			}

			this.fetch("POST", "/api/profile/user/search", {query: this.query}).then((res) => {
				this.error = res.error;
				this.results = res.results ?? [];
				this.search.show();
			});
		}
	}));
});
