document.addEventListener("alpine:init", () => {
	Alpine.data("index", () => ({
		draft: {
			body: "",
			media: null,
			interests: []
		},
		posts: [
			{
				info: {
					id: 1,
					user_id: 1337,
					user_handle: "ferris",
					user_name: "Ferris the Crab",	// TODO: Add link to profile on profile header
					user_pfp: "http://web.archive.org/web/20240409133415if_/https://rustacean.net/more-crabby-things/squishable-ferris.jpg",
					body: `The Rules say there may exist either:\n- one or more references\n- exactly one mutable reference`,
					media: "https://cat-milk.github.io/Anime-Girls-Holding-Programming-Books/static/f5bcf000a3399d76c369dffce060f941/72645/Tsukishima_Shijima_The_Rust_programming_language.png",
					date: "1970-01-01",
					likes: 12000,
					comments: 1000,
					user_like: false
				},
				comments: [],
				draft: ""
			}
		],

		submit_post() {
			let form = new FormData();
			form.append("json", JSON.stringify({
				body: this.draft.body,
				tags: this.draft.tags
			}));
			form.append("media", this.draft.media);

			this.fetch("PUT", "/api/post", form).then((res) => {
				console.log(res);
			});
		}
	}));
});
