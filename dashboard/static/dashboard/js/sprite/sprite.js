// const husky = document.getElementById('husky');
import { Standing, Running } from '../states/states.js';

export class Sprite {
  constructor(game) {
    this.game = game;
    this.sheet = document.getElementById(this.game.id);
    // this.sheet = husky;
    this.spriteWidth = 64;
    this.spriteHeight = 64;
    this.sizeFactor = 1;
    this.width = this.spriteWidth * this.sizeFactor;
    this.height = this.spriteHeight * this.sizeFactor;
    this.x = (this.game.width - this.width) / 2;
    this.y = this.game.height - this.height;
    this.frameX = 0;
    this.frameY = 1;
    this.maxFrame = 3;
    this.fps = 20;
    this.frameInterval = 1000 / this.fps;
    this.frameTimer = 0;
    this.states = [new Standing(this, this.game), new Running(this, this.game)];
    this.currentState = this.states[0];
    this.currentState.enter();
  }
  update(deltaTime) {
    if (this.frameTimer < this.frameInterval) this.frameTimer += deltaTime;
    else {
      this.frameTimer = 0;
      if (this.frameX < this.maxFrame) this.frameX++;
      else this.frameX = 0;
    }
  }
  draw(context) {
    context.drawImage(this.sheet, this.frameX * this.spriteWidth, this.frameY * this.spriteHeight, this.spriteWidth, this.spriteHeight, this.x, this.y, this.width, this.height);
  }
}