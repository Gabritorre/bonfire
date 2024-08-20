document.addEventListener("alpine:init", () => {
	Alpine.data("ads", () => ({
		id: null,
		draft: {
			name: null,
			link: null,
			probability: null
		},
		stats: {},
		ads: null,
		error: null,

		init() {
			const params = new URLSearchParams(window.location.search);
			this.id = +params.get("id");

			this.fetch("POST", "/api/profile/adv/ads", {id: this.id}).then((res) => {
				this.ads = (res.ads ?? []).reverse();
				this.ads.forEach((ad) => {
					if (this.stats.hasOwnProperty(ad.id)) {
						return;
					}

					this.fetch("POST", "/api/ad/stats", {id: ad.id}).then((res) => {
						if (res.error) {
							return;
						}
						this.stats[ad.id] = res.stats;
					});
				});
			});
		},

		submit_ad() {
			let form = new FormData();
			form.append("json", JSON.stringify({
				id: this.id,
				name: this.draft.name,
				link: this.draft.link,
				probability: this.draft.probability/100
			}));
			form.append("media", this.$refs.media.files[0]);

			this.fetch("PUT", "/api/ad", form).then((res) => {
				if (res.error) {
					this.error = res.error;
					return;
				}
				this.error = null;
				this.draft.name = null;
				this.draft.link = null;
				this.draft.probability = null;
				this.$refs.media.value = null;
				this.ads.splice(0, 0, res.ad);
			});
		},

		delete_ad(ad) {
			this.alert("Delete ad", "Are you sure you want to delete this ad?").then((confirmed) => {
				if (!confirmed) {
					return;
				}

				this.fetch("DELETE", "/api/ad", {
					id: ad.id
				}).then((res) => {
					if (res.error) {
						return;
					}
					const i = this.ads.indexOf(ad);
					if (i > -1) {
						this.ads.splice(i, 1);
					}
				});
			});
		}
	}));
});
