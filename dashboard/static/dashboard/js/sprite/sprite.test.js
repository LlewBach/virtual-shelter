import { Sprite } from './sprite.js';
import { Standing } from '../states/states.js';

describe('Sprite class', () => {
  let game, sprite, mockContext
  let mockImage = {};

  beforeEach(() => {
    game = {
      width: 200,
      height: 200,
      id: 1
    };
    sprite = new Sprite(game);
    mockContext = {
      drawImage: jest.fn()
    };
  });

  test('should create an instance of Sprite', () => {
    expect(sprite).toBeInstanceOf(Sprite);
  });

  test('should contain necessary keys', () => {
    expect(sprite).toHaveProperty('game');
    expect(sprite).toHaveProperty('sheet');
    expect(sprite).toHaveProperty('spriteWidth');
    expect(sprite).toHaveProperty('spriteHeight');
    expect(sprite).toHaveProperty('sizeFactor');
    expect(sprite).toHaveProperty('width');
    expect(sprite).toHaveProperty('height');
    expect(sprite).toHaveProperty('x');
    expect(sprite).toHaveProperty('y');
    expect(sprite).toHaveProperty('frameX');
    expect(sprite).toHaveProperty('frameY');
    expect(sprite).toHaveProperty('maxFrame');
    expect(sprite).toHaveProperty('fps');
    expect(sprite).toHaveProperty('frameInterval');
    expect(sprite).toHaveProperty('frameTimer');
    expect(sprite).toHaveProperty('states');
    expect(sprite).toHaveProperty('currentState');
  });

  test('should initialize with correct values', () => {
    expect(sprite.x).toBe((game.width - sprite.width) / 2);
    expect(sprite.y).toBe(game.height - sprite.height);
  });

  test('should start in the Standing state', () => {
    expect(sprite.currentState).toBeInstanceOf(Standing);
    expect(sprite.currentState).toBe(sprite.states[0]);
    expect(sprite.frameY).toBe(9);
  });

  test('.update should increment frameTimer if less than frameInterval', () => {
    sprite.frameTimer = 16;
    sprite.update(16);
    expect(sprite.frameTimer).toBe(32);
  });

  test('.update should reset frameTimer if more than frameInterval', () => {
    sprite.frameTimer = 50;
    sprite.update(16);
    expect(sprite.frameTimer).toBe(0);
  });

  test('.update should update frameX when update is called with enough deltaTime', () => {
    sprite.frameTimer = 0;
    sprite.update(16);
    // Less than frame interval, frameX should not change
    expect(sprite.frameX).toBe(0);
    // Enough time for frame to change
    sprite.frameTimer = 50;
    sprite.update(16);
    expect(sprite.frameX).toBe(1);
  });

  test('.update should reset frameX when maxFrame reached', () => {
    sprite.frameX = sprite.maxFrame;
    sprite.frameTimer = sprite.frameInterval;
    sprite.update(16);
    expect(sprite.frameX).toBe(0);
  });

  test('.draw should call context.drawImage correctly', () => {
    sprite.image = mockImage;
    sprite.draw(mockContext);
    expect(mockContext.drawImage).toHaveBeenCalledWith(sprite.sheet, sprite.frameX * sprite.spriteWidth, sprite.frameY * sprite.spriteHeight, sprite.spriteWidth, sprite.spriteHeight, sprite.x, sprite.y, sprite.width, sprite.height);
  });
});