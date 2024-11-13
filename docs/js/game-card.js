import { COMPATIBILITY } from "./medal-icons.js";

class GameCard {
  constructor(gameData) {
    this.data = gameData;
    this.template = document.getElementById("game-card-template");
  }

  getSteamDeckCompat() {
    const status = this.data.platforms.steamdeck.toLowerCase();
    return COMPATIBILITY[status] || COMPATIBILITY.unknown;
  }

  createCard() {
    const card = this.template.content.cloneNode(true);
    const container = card.querySelector(".game-card");

    // Set image if exists
    const img = card.querySelector(".game-image");
    if (this.data.header_image) {
      img.src = this.data.header_image;
      img.alt = this.data.title;
    } else {
      img.remove();
    }

    // Set title
    card.querySelector(".game-title").textContent = this.data.title;

    // Set rankings
    const rankings = [];
    if (this.data.rankings.RPS)
      rankings.push(`RPS: #${this.data.rankings.RPS}`);
    if (this.data.rankings.IGN)
      rankings.push(`IGN: #${this.data.rankings.IGN}`);
    if (this.data.rankings.PCGamer)
      rankings.push(`PCGamer: #${this.data.rankings.PCGamer}`);
    card.querySelector(".game-rankings").textContent = rankings.join(" | ");

    // Set platform tags
    this.setPlatformTag(card, "windows");
    this.setPlatformTag(card, "macos");
    this.setPlatformTag(card, "linux");
    this.setSteamDeckTag(card);

    // Set meta information
    if (this.data.user_score) {
      card.querySelector(".user-score").textContent =
        `User Score: ${(this.data.user_score * 100).toFixed(0)}%`;
    }
    card.querySelector(".price").textContent = this.data.price;

    return container;
  }

  setPlatformTag(card, platform) {
    const tag = card.querySelector(`[data-platform="${platform}"]`);
    tag.classList.add(
      this.data.platforms[platform] ? "available" : "unavailable",
    );
  }

  setSteamDeckTag(card) {
    const deckTag = card.querySelector(".steamdeck");
    const compat = this.getSteamDeckCompat();
    const medal = card.querySelector(".medal");

    deckTag.classList.add(compat.class);
    medal.innerHTML = `
            <svg class="medal-svg" width="16" height="16">
                <use href="${compat.icon}"/>
            </svg>
            Steam Deck: ${compat.text}
        `;
  }
}

export { GameCard };
