const SCROLL_THRESHOLD = 1000;	// TODO: Reduce with a faster db connection

document.addEventListener("alpine:init", () => {
	Alpine.data("feed", () => ({
		comments: {},
		drafts: {},
		fetching: false,

		init() {
			this.$watch("posts.length", () => {
				this.posts.forEach((post) => {
					if (post.type == "post" && !this.comments.hasOwnProperty(post.id)) {
						this.update_comments(post);
					}
					if (post.media) {
						this.blobify(post.media);
					}
				});
			});

			const scroll_handler = () => {
				const scroll = this.$refs.scroll;
				const delta = (scroll.scrollHeight - scroll.clientHeight) - scroll.scrollTop;
				if (delta <= SCROLL_THRESHOLD && !this.fetching) {
					this.fetching = true;
					this.continue_posts().then(() => this.fetching = false);
				}
			}
			this.$refs.scroll?.addEventListener("scroll", scroll_handler);
			scroll_handler();
		},

		continue_posts() {
			const user_posts = this.posts.filter((post) => post.type === "post");
			return this.fetch_feed(user_posts[user_posts.length-1]?.id ?? null, this.posts);
		},

		update_comments(post) {
			return this.fetch("POST", "/api/post/comments", {
				id: post.id
			}).then((res) => {
				if (res.error) {
					return res;
				}
				this.comments[post.id] = res.comments.reverse();
				post.comments = this.comments[post.id].length;
				return res;
			});
		},

		submit_like(post) {
			this.fetch(
				post.user_like ? "DELETE" : "PUT",
				"/api/post/like",
				{id: post.id}
			).then((res) => {
				if (res.error) {
					return;
				}
				post.likes += post.user_like ? -1 : 1;
				post.user_like = !post.user_like;
			});
		},

		submit_comment(post) {
			this.fetch("PUT", "/api/post/comment", {
				id: post.id,
				body: this.drafts[post.id]
			}).then((res) => {
				if (res.error) {
					return res;
				}
				return this.update_comments(post);
			}).then((res) => {
				if (res.error) {
					return;
				}
				this.drafts[post.id] = null;
			});
		},

		delete_post(post) {
			this.alert("Delete post", "Are you sure you want to delete this post?").then((confirmed) => {
				if (!confirmed) {
					return;
				}

				this.fetch("DELETE", "/api/post", {
					id: post.id
				}).then((res) => {
					if (res.error) {
						return;
					}
					const i = this.posts.indexOf(post);
					if (i > -1) {
						this.posts.splice(i, 1);
					}
				});
			});
		},

		delete_comment(post, comment) {
			this.alert("Delete comment", "Are you sure you want to delete this comment?").then((confirmed) => {
				if (!confirmed) {
					return;
				}

				this.fetch("DELETE", "/api/post/comment", {id: comment.id}).then((res) => {
					if (res.error) {
						return;
					}
					const i = this.comments[post.id].indexOf(comment);
					if (i > -1) {
						this.comments[post.id].splice(i, 1);
						post.comments = this.comments[post.id].length;
					}
				});
			});
		}
	}));
});
