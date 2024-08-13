document.addEventListener("alpine:init", () => {
	Alpine.data("index", () => ({
		draft: {
			body: "",
			tags: []
		},
		posts: [],

		post() {
			let form = new FormData();
			form.append("json", JSON.stringify({
				body: this.draft.body,
				tags: this.draft.tags
			}));
			form.append("media", this.$refs.media.files[0]);

			this.fetch("PUT", "/api/post", form).then((res) => {
				console.log(res);
			});
		}
	}));
});
