import { Sprite } from '../sprite/sprite.js';

export class Game {
  constructor(width, height, id) {
    this.width = width;
    this.height = height;
    this.id = id;
    this.sprite = new Sprite(this);
  }
  update(deltaTime) {
    this.sprite.update(deltaTime);
  }
  draw(context) {
    this.sprite.draw(context);
  }
}

window.addEventListener('load', function () {
  const canvases = document.querySelectorAll('canvas');
  canvases.forEach(canvas => {
    canvas.width = 200;
    canvas.height = 200;
    const ctx = canvas.getContext('2d');
    const id = canvas.getAttribute('data-id');
    const game = new Game(canvas.width, canvas.height, id);
    let lastTimeAnimate = 0;

    function animate(timestamp) {
      ctx.clearRect(0, 0, game.width, game.height);
      const deltaTime = timestamp - lastTimeAnimate;
      lastTimeAnimate = timestamp;
      game.update(deltaTime);
      game.draw(ctx);
      requestAnimationFrame(animate);
    }

    animate(0);
  });
});