export class Standing {
  constructor(sprite, game) {
    this.sprite = sprite;
    this.game = game;
  }
  enter() {
    if (["husky/one", "husky/two", "husky/three"].includes(this.game.url)) {
      this.sprite.spriteWidth = 64;
      this.sprite.maxFrame = 4;
    } else if (["afghan/one", "afghan/two", "afghan/three"].includes(this.game.url)) {
      this.sprite.spriteWidth = 64;
      this.sprite.maxFrame = 2;
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
    if (["husky/one", "husky/two"].includes(this.game.url)) {
      this.sprite.spriteWidth = 74;
    } else {
      this.sprite.spriteWidth = 76;
    }
    this.sprite.maxFrame = 7;
    this.sprite.frameX = 0;
    this.sprite.frameY = 6;
  }
}
