document.addEventListener("alpine:init", () => {
	Alpine.data("feed", () => ({
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
				// TODO: Add comment on top of comments list
			});
		}
	}));
});
