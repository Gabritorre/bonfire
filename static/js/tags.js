document.addEventListener("alpine:init", () => {
	Alpine.data("tags", () => ({
		all: [],
		remaining: [],

		init() {
			this.$watch("interests", () => this.tags_update());

			this.fetch("GET", "/api/tags").then((res) => {
				if (res.error) {
					return;
				}
				this.all = res.tags ?? [];
				this.remaining = this.all;
				this.tags_update();
			});
		},

		tags_update() {
			const ids = this.interests.map((tag) => tag.id);
			this.remaining = this.all.filter((tag) => !ids.includes(tag.id));
		},

		tag_add(i) {
			const tag = this.remaining.splice(i, 1)[0];
			this.interests.push(tag);
		},

		tag_remove(i) {
			const tag = this.interests.splice(i, 1)[0];
			this.remaining.push(tag);
		}
	}));
});
