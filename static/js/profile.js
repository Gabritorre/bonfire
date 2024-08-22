document.addEventListener("alpine:init", () => {
	Alpine.data("profile", () => ({
		id: null,
		user: {},
		posts: [],

		init() {
			const params = new URLSearchParams(window.location.search);
			this.id = +params.get("id");
			this.fetch("POST", "/api/profile/user", {id: this.id}).then((res) => {
				if (res.error) {
					return;
				}

				this.user = res.user;
				this.user.pfp ??= PFP_EMPTY;
				this.user.gender &&= this.user.gender.charAt(0).toUpperCase() + this.user.gender.slice(1);
			});
		},

		fetch_feed(last_post_id) {
			return this.fetch("POST", "/api/feed/user", {
				id: this.id,
				last_post_id: last_post_id
			}).then((res) => {
				if (res.error) {
					return res;
				}
				this.posts.push(...res.posts.map((post) => ({type: "post", ...post})));
				return res;
			});
		},

		submit_follow() {
			this.fetch(
				this.user.followed ? "DELETE" : "PUT",
				"/api/profile/user/follow",
				{id: this.id}
			).then((res) => {
				if (res.error) {
					return;
				}
				this.user.follower += this.user.followed ? -1 : 1;
				this.user.followed = !this.user.followed;
			});
		}
	}));
});
