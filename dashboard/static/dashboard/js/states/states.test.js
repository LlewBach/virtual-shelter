import { Standing, Running } from './states.js';

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

describe('Running State', () => {
  let runningState;

  beforeEach(() => {
    runningState = new Running(sprite, game);
  });

  test('should configure some sprite properties on enter', () => {
    runningState.enter();
    expect(sprite.spriteWidth).toBe(74);
    expect(sprite.maxFrame).toBe(7);
    expect(sprite.frameX).toBe(0);
    expect(sprite.frameY).toBe(6);
  });
});
