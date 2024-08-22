document.addEventListener("alpine:init", () => {
	Alpine.data("campaigns", () => ({
		draft: {
			name: null,
			start: null,
			end: null,
			interests: []
		},
		campaigns: null,
		error: null,
		budget_addition: null,

		init() {
			this.fetch("POST", "/api/profile/adv/campaigns").then((res) => {
				this.campaigns = (res.campaigns ?? []).sort((a, b) => b.id - a.id);
			});
		},

		submit_campaign() {
			this.fetch("PUT", "/api/profile/adv/campaign", {
				name: this.draft.name,
				start: this.draft.start,
				end: this.draft.end,
				tags: this.draft.interests.map((tag) => tag.id)
			}).then((res) => {
				if (res.error) {
					this.error = res.error;
					return;
				}
				this.error = null;
				this.campaigns.splice(0, 0, res.campaign);
				this.draft.name = null;
				this.draft.start = null;
				this.draft.end = null;
				this.draft.interests.splice(0);
			});
		},

		delete_campaign(campaign) {
			this.alert("Delete campaign", "Are you sure you want to delete this campaign?").then((confirmed) => {
				if (!confirmed) {
					return;
				}

				this.fetch("DELETE", "/api/profile/adv/campaign", {
					id: campaign.id
				}).then((res) => {
					if (res.error) {
						return;
					}
					const i = this.campaigns.indexOf(campaign);
					if (i > -1) {
						this.campaigns.splice(i, 1);
					}
				})
			});
		},

		update_budget(campaign) {
			this.budget_addition = 10;
			this.alert("Buy credits", null).then((confirmed) => {
				const addition = +this.budget_addition;
				this.budget_addition = null;
				if (!confirmed) {
					return;
				}

				this.fetch("PUT", "/api/profile/adv/budget", {
					id: campaign.id,
					funds: addition
				}).then((res) => {
					if (res.error) {
						return;
					}
					campaign.budget += addition;
					campaign.total_budget += addition;
				});
			});
		}
	}));
});
