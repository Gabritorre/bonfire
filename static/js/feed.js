document.addEventListener("alpine:init", () => {
	Alpine.data("feed", () => ({
		fetched: [],

		init() {
			this.$watch("posts", () => this.comments_update());
			this.comments_update();
		},

		comments_update() {
			for (let i = 0; i < this.posts.length; i++) {
				let post = this.posts[i];
				if (this.fetched.includes(post.info.id)) {
					continue;
				}
				this.fetched.push(post.info.id);

				this.fetch("POST", "/api/post/comments", {
					id: post.info.id
				}).then((res) => {
					if (res.error) {
						return;
					}
					post.draft = "";
					post.comments = res.comments.reverse();
				});
			}
		},

		submit_like(i) {
			const info = this.posts[i].info;
			this.fetch(
				info.user_like ? "DELETE" : "PUT",
				"/api/post/like",
				{id: info.id}
			).then((res) => {
				if (res.error) {
					return;
				}
				info.user_like = !info.user_like;
			});
		},

		submit_comment(i) {
			const post = this.posts[i];
			this.fetch("PUT", "/api/post/comment", {
				id: post.info.id,
				body: post.draft
			}).then((res) => {
				let j = this.fetched.indexOf(post.info.id);
				if (j >= 0) {
					this.fetched.splice(j, 1);
				}
				this.comments_update();
			});
		}
	}));
});
