const STATS_MAX_DAYS = 40;

document.addEventListener("alpine:init", () => {
	Alpine.data("ads", () => ({
		id: null,
		draft: {
			name: null,
			link: null,
			probability: null
		},
		stats: {},
		charts: [],
		ads: null,
		error: null,

		init() {
			Chart.defaults.color = "#7e7e7e";
			Chart.defaults.borderColor = "#333";

			const params = new URLSearchParams(window.location.search);
			this.id = +params.get("id");

			this.$watch("ads?.length", () => {
				this.charts.forEach((chart) => chart.destroy());
				this.charts.splice(0);
				this.ads.forEach((ad) => {
					this.blobify(ad.media);
					this.create_chart(ad);
				});
			});

			this.fetch("POST", "/api/profile/adv/ads", {id: this.id}).then((res) => {
				this.ads = (res.ads ?? []).sort((a, b) => b.id - a.id);
			});
		},

		fetch_stats(ad) {
			if (this.stats.hasOwnProperty(ad.id)) {
				return new Promise((resolve) => resolve());
			}

			return this.fetch("POST", "/api/ad/stats", {id: ad.id}).then((res) => {
				const fetched_stats = new Map((res.stats ?? []).map((stat) => [new Date(stat.date).getTime(), stat]));

				const first_day = Math.min(...fetched_stats.keys()), last_day = Math.max(...fetched_stats.keys());
				const stats = Array.from({length: Math.min(STATS_MAX_DAYS, (last_day-first_day)/(24*60*60*1000)+1)}).map((_, i) => {
					const date = last_day - i*24*60*60*1000;
					return fetched_stats.get(date) ?? {
						date: date,
						clicks: 0,
						impressions: 0,
						readings: 0
					};
				}).reverse();

				const labels = stats.map((stat) => {
					const date = new Date(stat.date);
					const month = date.toLocaleString([], {month: "short"});
					const day = date.getDate();
					return month + " " + day;
				});

				this.stats[ad.id] = {
					labels: labels,
					datasets: [
						{
							label: "Clicks",
							data: stats.map((stat) => stat.clicks)
						},
						{
							label: "Impressions",
							data: stats.map((stat) => stat.impressions)
						},
						{
							label: "Readings",
							data: stats.map((stat) => stat.readings)
						}
					]
				};
			});
		},

		create_chart(ad) {
			const i = this.ads.indexOf(ad);
			if (i < 0) {
				return;
			}

			this.fetch_stats(ad).then(() => {
				if (this.ads[i] !== ad) {
					return;
				}

				const canvas = document.querySelectorAll(".card canvas")[i];
				this.charts.push(new Chart(canvas, {
					type: "line",
					data: this.stats[ad.id]
				}));
			})
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
