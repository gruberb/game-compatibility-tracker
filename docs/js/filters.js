class GameFilters {
  constructor(updateCallback) {
    this.filters = {
      platforms: [],
      stores: [],
      search: "",
      minMetacritic: 0,
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

    // Store filters
    document.querySelectorAll("[data-store]").forEach((checkbox) => {
      checkbox.addEventListener("change", (e) => {
        const store = e.target.dataset.store;
        if (e.target.checked) {
          this.filters.stores.push(store);
        } else {
          this.filters.stores = this.filters.stores.filter((s) => s !== store);
        }
        this.updateCallback();
      });
    });

    // Metacritic filter
    const metacriticSlider = document.getElementById("metacritic-filter");
    if (metacriticSlider) {
      metacriticSlider.addEventListener("input", (e) => {
        this.filters.minMetacritic = parseInt(e.target.value);
        document.getElementById("metacritic-value").textContent =
          this.filters.minMetacritic;
        this.updateCallback();
      });
    }
  }

  calculatePoints(game) {
    let points = 0;
    if (game.rankings.RPS) points += 101 - game.rankings.RPS;
    if (game.rankings.IGN) points += 101 - game.rankings.IGN;
    if (game.rankings.PCGamer) points += 101 - game.rankings.PCGamer;
    if (game.metacritic) points += game.metacritic;
    return points;
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

      // Store filters
      const storeMatch =
        this.filters.stores.length === 0 ||
        this.filters.stores.every((store) =>
          game.stores.some((gameStore) =>
            gameStore.toLowerCase().includes(store.toLowerCase()),
          ),
        );

      // Metacritic filter
      const metacriticMatch =
        !this.filters.minMetacritic ||
        (game.metacritic && game.metacritic >= this.filters.minMetacritic);

      // Search filter
      const searchMatch =
        this.filters.search === "" ||
        game.title.toLowerCase().includes(this.filters.search.toLowerCase());

      return platformMatch && searchMatch && storeMatch && metacriticMatch;
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
        case "metacritic":
          return (b.metacritic || 0) - (a.metacritic || 0);
        case "release":
          return new Date(b.release_date || 0) - new Date(a.release_date || 0);
        case "points":
          return this.calculatePoints(b) - this.calculatePoints(a);
        default:
          return 0;
      }
    });
  }
}

export { GameFilters };
