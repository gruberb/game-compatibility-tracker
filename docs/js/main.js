import { GameCard } from "./game-card.js";
import { GameFilters } from "./filters.js";

class GameApp {
  constructor() {
    this.games = [];
    this.gameGrid = document.getElementById("game-grid");
    this.visibleCountEl = document.getElementById("visible-count");
    this.totalCountEl = document.getElementById("total-count");

    this.filters = new GameFilters(() => this.updateDisplay());
    this.loadGames();
  }

  async loadGames() {
    try {
      const response = await fetch("data/merged_games.json");
      this.games = await response.json();
      this.totalCountEl.textContent = this.games.length;
      this.updateDisplay();
    } catch (error) {
      console.error("Error loading games:", error);
      this.gameGrid.innerHTML =
        "<p>Error loading games data. Please try again later.</p>";
    }
  }

  updateDisplay() {
    // Filter and sort games
    let displayedGames = this.filters.filterGames(this.games);
    displayedGames = this.filters.sortGames(displayedGames);

    // Update stats
    this.visibleCountEl.textContent = displayedGames.length;

    // Clear and rebuild game grid
    this.gameGrid.innerHTML = "";
    displayedGames.forEach((gameData) => {
      const gameCard = new GameCard(gameData);
      this.gameGrid.appendChild(gameCard.createCard());
    });
  }
}

// Initialize app when DOM is loaded
window.addEventListener("DOMContentLoaded", () => {
  new GameApp();
});
