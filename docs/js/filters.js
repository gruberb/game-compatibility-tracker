class GameFilters {
  constructor(updateCallback) {
    this.filters = {
      platforms: [],
      search: "",
    };
    this.sortBy = "title";
    this.updateCallback = updateCallback;
    this.setupEventListeners();
  }

  setupEventListeners() {
    // Search
    document.getElementById("search").addEventListener("input", (e) => {
      this.filters.search = e.target.value;
      this.updateCallback();
    });

    // Sort
    document.getElementById("sort-by").addEventListener("change", (e) => {
      this.sortBy = e.target.value;
      this.updateCallback();
    });

    // Platform filters
    document.querySelectorAll("[data-platform]").forEach((checkbox) => {
      checkbox.addEventListener("change", (e) => {
        const platform = e.target.dataset.platform;
        if (e.target.checked) {
          this.filters.platforms.push(platform);
        } else {
          this.filters.platforms = this.filters.platforms.filter(
            (p) => p !== platform,
          );
        }
        this.updateCallback();
      });
    });
  }

  filterGames(games) {
    return games.filter((game) => {
      // Platform filters
      const platformMatch =
        this.filters.platforms.length === 0 ||
        this.filters.platforms.every((platform) => {
          if (platform === "steamdeck") {
            const status = game.platforms.steamdeck.toLowerCase();
            return ["platinum", "gold"].includes(status);
          }
          return game.platforms[platform];
        });

      // Search filter
      const searchMatch =
        this.filters.search === "" ||
        game.title.toLowerCase().includes(this.filters.search.toLowerCase());

      return platformMatch && searchMatch;
    });
  }

  sortGames(games) {
    return games.sort((a, b) => {
      switch (this.sortBy) {
        case "title":
          return a.title.localeCompare(b.title);
        case "rps":
          return (a.rankings.RPS || 999) - (b.rankings.RPS || 999);
        case "ign":
          return (a.rankings.IGN || 999) - (b.rankings.IGN || 999);
        case "pcgamer":
          return (a.rankings.PCGamer || 999) - (b.rankings.PCGamer || 999);
        case "score":
          return (b.user_score || 0) - (a.user_score || 0);
        default:
          return 0;
      }
    });
  }
}

export { GameFilters };
