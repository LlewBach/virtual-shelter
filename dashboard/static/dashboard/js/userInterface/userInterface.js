export class UserInterface {
  constructor(game) {
    this.game = game;
  }
  draw(context) {
    // Satiation Bar
    context.fillStyle = '#d8d9f7';
    context.fillText('Satiation: ' + this.game.satiation, 5, 15);
    context.fillRect(65, 8, this.game.satiation, 6);
  }
}