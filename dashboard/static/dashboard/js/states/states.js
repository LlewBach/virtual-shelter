export class Standing {
  constructor(sprite, game) {
    this.sprite = sprite;
    this.game = game;
  }
  enter() {
    this.sprite.spriteWidth = 64;
    if (["husky/one", "husky/two", "husky/three"].includes(this.game.url)) {
      this.sprite.maxFrame = 4;
    } else if (["afghan/one", "afghan/two", "afghan/three", "shiba/one", "shiba/two", "shiba/three", "doberman/one", "doberman/two", "doberman/three"].includes(this.game.url)) {
      this.sprite.maxFrame = 2;
    } else if (["bloodhound/one", "bloodhound/two", "bloodhound/three", "greyhound/one", "greyhound/two", "greyhound/three", "greatdane/one", "greatdane/three"].includes(this.game.url)) {
      this.sprite.maxFrame = 3;
    } else if (["dalmatian/one", "dalmatian/two", "dalmatian/three"].includes(this.game.url)) {
      this.sprite.maxFrame = 7;
    } else if (["alsatian/one", "alsatian/two", "alsatian/three"].includes(this.game.url)) {
      this.sprite.maxFrame = 4;
      this.sprite.spriteWidth = 67;
    } else if (["greatdane/two", "mountain/one", "mountain/two", "mountain/three"].includes(this.game.url)) {
      this.sprite.maxFrame = 3;
      this.sprite.spriteWidth = 65;
    }
    this.sprite.frameX = 0;
    this.sprite.frameY = 9;
  }
}

export class Running {
  constructor(sprite, game) {
    this.sprite = sprite;
    this.game = game;
  }
  enter() {
    if (["dalmatian/two", "dalmatian/three"].includes(this.game.url)) {
      this.sprite.spriteWidth = 65
    } else if (["shiba/one", "shiba/two", "shiba/three"].includes(this.game.url)) {
      this.sprite.spriteWidth = 71;
    } else if (["dalmatian/one"].includes(this.game.url)) {
      this.sprite.spriteWidth = 72;
    } else if (["husky/one", "husky/two"].includes(this.game.url)) {
      this.sprite.spriteWidth = 74;
    } else if (["greyhound/one", "greyhound/two", "greyhound/three"].includes(this.game.url)) {
      this.sprite.spriteWidth = 75;
    } else if (["husky/three", "afghan/one", "afghan/two", "afghan/three"].includes(this.game.url)) {
      this.sprite.spriteWidth = 76;
    } else if (["bloodhound/one", "bloodhound/three"].includes(this.game.url)) {
      this.sprite.spriteWidth = 77;
    } else if (["bloodhound/two", "doberman/one", "doberman/two", "doberman/three"].includes(this.game.url)) {
      this.sprite.spriteWidth = 78;
    } else if (["alsatian/one", "alsatian/two", "alsatian/three"].includes(this.game.url)) {
      this.sprite.spriteWidth = 80;
    } else if (["mountain/one", "mountain/two", "mountain/three"].includes(this.game.url)) {
      this.sprite.spriteWidth = 91;
    } else if (["greatdane/two"].includes(this.game.url)) {
      this.sprite.spriteWidth = 94;
    } else if (["greatdane/one", "greatdane/three"].includes(this.game.url)) {
      this.sprite.spriteWidth = 95;
    }
    this.sprite.maxFrame = 7;
    this.sprite.frameX = 0;
    this.sprite.frameY = 6;
  }
}
