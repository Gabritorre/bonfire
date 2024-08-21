document.addEventListener("alpine:init", () => {
	Alpine.data("index", () => ({
		draft: {
			body: null,
			interests: []
		},
		friends: [],
		explore: [],
		feed: "explore",

		fetch_feed(last_post_id, source) {
			let original_feed = source == this.friends ? "friends" : "explore";
			return this.fetch("POST", "/api/feed/" + original_feed, {last_post_id}).then((res) => {
				if (res.error) {
					return res;
				}

				this[original_feed].push(...res.posts.map((post) => ({type: "post", ...post})));
				if (res.ad) {
					this[original_feed].push({type: "ad", ...res.ad});
				}
				return res;
			});
		},

		submit_post() {
			let form = new FormData();
			form.append("json", JSON.stringify({
				body: this.draft.body,
				tags: this.draft.interests.map((tag) => tag.id)
			}));
			form.append("media", this.$refs.media.files[0]);

			this.fetch("PUT", "/api/post", form).then((res) => {
				if (res.error) {
					return;
				}
				this.explore.splice(0, 0, {type: "post", ...res.post});
				this.draft.body = null;
				this.$refs.media.value = null;
				this.draft.interests.splice(0);
			});
		}
	}));
});
