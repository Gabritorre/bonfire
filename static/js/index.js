document.addEventListener("alpine:init", () => {
	Alpine.data("index", () => ({
		draft: {
			body: "",
			interests: []
		},
		friends: [],
		explore: [],
		posts: null,
		feed: "explore",

		init() {
			this.posts = this[this.feed];
			this.$watch("feed", () => {
				this.posts = this[this.feed];
				if (this.posts.length == 0) {
					this.fetch_feed(null);
				}
			});
		},

		fetch_feed(last_post_id) {
			let original_feed = this.feed;
			return this.fetch("POST", "/api/feed/" + this.feed, {last_post_id}).then((res) => {
				if (res.error || original_feed != this.feed) {
					return res;
				}

				this.posts.push(...res.posts.map((post) => ({type: "post", ...post})));
				if (res.ad) {
					this.posts.push({type: "ad", ...res.ad});
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
				this.posts.splice(0, 0, {type: "post", ...res.post});
				this.draft.body = "";
				this.$refs.media.value = null;
				this.draft.interests.splice(0);
			});
		}
	}));
});
