// game-card.js
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

    // Image section
    const img = card.querySelector(".game-image");
    if (this.data.header_image) {
      img.src = this.data.header_image;
    } else {
      img.src =
        'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 150"%3E%3Crect width="320" height="150" fill="%23f3f4f6"/%3E%3Ctext x="160" y="75" fill="%239ca3af" font-family="sans-serif" font-size="14" text-anchor="middle" dominant-baseline="middle"%3E%3C/text%3E%3C/svg%3E';
    }
    img.alt = this.data.title;

    // Title
    card.querySelector(".game-title").textContent = this.data.title;

    // Rankings
    const rankings = [];
    if (this.data.rankings.RPS)
      rankings.push(`RPS: #${this.data.rankings.RPS}`);
    if (this.data.rankings.IGN)
      rankings.push(`IGN: #${this.data.rankings.IGN}`);
    if (this.data.rankings.PCGamer)
      rankings.push(`PCGamer: #${this.data.rankings.PCGamer}`);
    card.querySelector(".game-rankings").textContent = rankings.join(" | ");

    // Platforms
    this.setPlatformTag(card, "windows");
    this.setPlatformTag(card, "macos");
    this.setPlatformTag(card, "linux");
    this.setPlatformTag(card, "switch");
    this.setSteamDeckTag(card);

    // Stores
    this.setStores(card);

    // Meta information
    this.setMetaInformation(card);

    return container;
  }

  setPlatformTag(card, platform) {
    const tag = card.querySelector(`[data-platform="${platform}"]`);
    if (tag) {
      tag.classList.add(
        this.data.platforms[platform] ? "available" : "unavailable",
      );
    }
  }

  setSteamDeckTag(card) {
    const deckTag = card.querySelector(".steamdeck");
    const compat = this.getSteamDeckCompat();
    const medal = card.querySelector(".medal");

    if (this.data.steam_id && this.data.platforms.steamdeck !== "unknown") {
      const protonLink = document.createElement("a");
      protonLink.href = `https://www.protondb.com/app/${this.data.steam_id}`;
      protonLink.target = "_blank";
      protonLink.className = `platform-tag steamdeck ${compat.class}`;
      protonLink.innerHTML = `
                <svg class="medal-svg" width="16" height="16">
                    <use href="${compat.icon}"/>
                </svg>
                Steam Deck: ${compat.text}
            `;
      deckTag.replaceWith(protonLink);
    } else {
      deckTag.classList.add(compat.class);
      medal.innerHTML = `
                <svg class="medal-svg" width="16" height="16">
                    <use href="${compat.icon}"/>
                </svg>
                Steam Deck: ${compat.text}
            `;
    }
  }

  setStores(card) {
    const storeList = card.querySelector(".store-tags");
    if (storeList && this.data.stores && this.data.stores.length > 0) {
      this.data.stores.forEach((store) => {
        const storeTag = document.createElement("span");
        storeTag.className = "store-tag";
        storeTag.textContent = store;
        storeList.appendChild(storeTag);
      });
    }
  }

  setMetaInformation(card) {
    // Price
    const priceElement = card.querySelector(".price");
    if (this.data.steam_id) {
      const priceLink = document.createElement("a");
      priceLink.href = `https://store.steampowered.com/app/${this.data.steam_id}`;
      priceLink.target = "_blank";
      priceLink.className = "steam-link";
      priceLink.textContent = this.data.price || "View on Steam";
      priceElement.appendChild(priceLink);
    } else {
      priceElement.textContent = this.data.price || "N/A";
    }

    // User Score
    const userScoreElement = card.querySelector(".user-score");
    if (this.data.user_score) {
      userScoreElement.textContent = `${(this.data.user_score * 100).toFixed(0)}% positive`;
    }

    // Metacritic Score
    const metacriticElement = card.querySelector(".metacritic");
    if (metacriticElement && this.data.metacritic) {
      metacriticElement.textContent = `Metacritic: ${this.data.metacritic}`;
    }

    // Release Date
    const releaseDateElement = card.querySelector(".release-date");
    if (releaseDateElement && this.data.release_date) {
      const date = new Date(this.data.release_date);
      releaseDateElement.textContent = date.toLocaleDateString();
    }
  }
}

export { GameCard };
