const SCROLL_THRESHOLD = 800;	// TODO: Reduce with a faster db connection
const INTERSECTION_UPDATE = 250;
const READING_DELAY = 3000;

document.addEventListener("alpine:init", () => {
	Alpine.data("feed", () => ({
		comments: {},
		drafts: {},
		interval: null,
		fetching: false,
		children: [],
		readings: {},
		read: [],

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
				this.children = this.$refs.feed.querySelectorAll(":scope > div:has(> .row)");
				this.readings.id = null;
			});

			const scroll_handler = (allow_hidden) => {
				if (!allow_hidden && !this.$refs.feed.offsetParent) {
					return;
				}
				const scroll = this.$refs.scroll;
				const delta = (scroll.scrollHeight - scroll.clientHeight) - scroll.scrollTop;
				if (delta <= SCROLL_THRESHOLD) {
					this.continue_posts();
				}
			};
			this.$refs.scroll.addEventListener("scroll", () => scroll_handler(false));
			scroll_handler(true);

			this.interval = setInterval(() => {
				const parent_box = this.$refs.scroll.getBoundingClientRect();
				const parent_center = {
					x: parent_box.left + parent_box.width/2,
					y: parent_box.top + parent_box.height/2
				};

				let found_visible = false;
				let closest_ad = null;
				let closest_distance = Infinity;
				for (let i = 0; i < this.children.length; i++) {
					if (this.posts[i].type != "ad") {
						continue;
					} else if (!this.children[i].offsetParent) {	// Ignore hidden elements
						continue;
					} else if (this.read.includes(this.posts[i].id)) {	// Ignore elements that were already seen
						continue;
					}

					const child_box = this.children[i].getBoundingClientRect();
					const child_center = {
						x: child_box.left + child_box.width/2,
						y: child_box.top + child_box.height/2
					};

					const visible = (
						child_center.x >= parent_box.left &&
						child_center.x <= parent_box.right &&
						child_center.y >= parent_box.top &&
						child_center.y <= parent_box.bottom
					);
					if (!visible && found_visible) {
						break;
					} else if (!visible) {
						continue;
					}

					found_visible = true;
					const distance = Math.sqrt((child_center.x - parent_center.x)**2 + (child_center.y - parent_center.y)**2);
					if (distance < closest_distance) {
						closest_distance = distance;
						closest_ad = i;
					}
				}

				if (!closest_ad) {
					this.readings.id = null;	// Timer needs to restart next time the ad is visible
					return;
				}

				const id = this.posts[closest_ad].id;
				this.readings.end = Date.now();
				if (this.readings.id !== id) {
					this.readings.id = id;
					this.readings.start = Date.now();

					setTimeout(() => {
						if (this.readings.id !== id) {
							return;
						}

						const delta = this.readings.end - this.readings.start;
						if (delta+INTERSECTION_UPDATE >= READING_DELAY) {
							this.fetch("PUT", "/api/ad/stats", {
								id: id,
								clicked: 0,
								read: 1
							}).then((res) => {
								if (res.error) {
									return;
								}
								this.read.push(id);
							});
						}
					}, READING_DELAY);
				}
			}, INTERSECTION_UPDATE);
		},

		click_ad(ad) {
			this.fetch("PUT", "/api/ad/stats", {id: ad.id, clicked: 1, read: 0});
		},

		continue_posts() {
			if (this.fetching) {
				return;
			}

			this.fetching = true;
			const user_posts = this.posts.filter((post) => post.type === "post");
			return this.fetch_feed(user_posts[user_posts.length-1]?.id ?? null, this.posts).then(() => {
				this.fetching = false;
			});
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
