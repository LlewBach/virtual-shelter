import { UserInterface } from '../userInterface/userInterface.js';
import { Sprite } from '../sprite/sprite.js';
import { feedSprite } from '../AJAX/button1.js';
import { ChartClass } from '../chart/chart.js';

export class Game {
  constructor(width, height, id, url) {
    this.width = width;
    this.height = height;
    this.id = id;
    this.url = url;
    this.userInterface = new UserInterface(this);
    this.sprite = new Sprite(this);
    this.satiation = 55;
    this.chartObj = new ChartClass(this.id);

    this.fetchStatus();
    this.statusInterval = setInterval(() => this.fetchStatus(), 61000);
  }
  fetchStatus() {
    fetch(`/dashboard/sprite/${this.id}/update-status/`)
      .then(response => response.json())
      .then(data => {
        this.satiation = data.satiation;
        this.sprite.setState(data.current_state);
        this.chartObj.updateChart(data);
      });
  }
  update(deltaTime) {
    this.sprite.update(deltaTime);
  }
  draw(context) {
    this.userInterface.draw(context);
    this.sprite.draw(context);
  }
}

window.addEventListener('load', function () {
  const spriteCanvases = document.querySelectorAll('.sprite-canvas');
  spriteCanvases.forEach(canvas => {
    canvas.width = 300;
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

