import { Standing } from './states.js';

const states = {
  STANDING: 0,
}

let sprite, game;

beforeEach(() => {
  sprite = {
    spriteWidth: undefined,
    frameX: undefined,
    maxFrame: undefined,
    frameY: undefined,
  };
  game = {
    url: 'husky/one'
  };
});

describe('Standing State', () => {
  let standingState;

  beforeEach(() => {
    standingState = new Standing(sprite, game);
  });

  test('should configure some sprite properties on .enter', () => {
    standingState.enter();
    expect(sprite.spriteWidth).toBe(64);
    expect(sprite.maxFrame).toBe(4);
    expect(sprite.frameX).toBe(0);
    expect(sprite.frameY).toBe(9);
  });
});
