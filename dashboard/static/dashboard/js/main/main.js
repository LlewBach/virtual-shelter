import { UserInterface } from '../userInterface/userInterface.js';
import { Sprite } from '../sprite/sprite.js';
import { feedSprite, getCSRFToken } from '../AJAX/button1.js';

export class Game {
  constructor(width, height, id, url) {
    this.width = width;
    this.height = height;
    this.id = id;
    this.url = url;
    this.satiation = 55;
    this.userInterface = new UserInterface(this);
    this.sprite = new Sprite(this);

    this.fetchStatus();
    this.statusInterval = setInterval(() => this.fetchStatus(), 61000);
  }
  fetchStatus() {
    fetch(`/dashboard/sprite/${this.id}/update-status/`)
      .then(response => response.json())
      .then(data => {
        this.satiation = data.satiation;
      })
  }
  // destroy() {
  //   clearInterval(this.statusInterval);
  // }
  update(deltaTime) {
    this.sprite.update(deltaTime);
  }
  draw(context) {
    this.userInterface.draw(context);
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
    const url = canvas.getAttribute('data-url');
    const game = new Game(canvas.width, canvas.height, id, url);
    let lastTimeAnimate = 0;

    // Manual test
    function animate(timestamp) {
      ctx.clearRect(0, 0, game.width, game.height);
      const deltaTime = timestamp - lastTimeAnimate;
      lastTimeAnimate = timestamp;
      game.update(deltaTime);
      game.draw(ctx);
      requestAnimationFrame(animate);
    }

    animate(0);

    // Manual test
    const feedButton = document.querySelector(`#button1-${id}`);
    feedButton.addEventListener('click', async () => {
      await feedSprite(id);
      game.fetchStatus();
    });
  });
});

