import { Game } from './main.js';
import { Sprite } from '../sprite/sprite.js';

// Mock dependencies
jest.mock('../sprite/sprite.js');

describe('Game class', () => {
  let game, mockContext;

  beforeEach(() => {
    game = new Game(200, 200, 1);
    mockContext = {
      drawImage: jest.fn()
    };
  });

  test('should create an instance of Game', () => {
    expect(game).toBeInstanceOf(Game);
  });

  test('should contain necessary keys', () => {
    expect(game).toHaveProperty('width');
    expect(game).toHaveProperty('height');
    expect(game).toHaveProperty('id');
  });

  test('should initialize with class instances', () => {
    expect(game.sprite).toBeInstanceOf(Sprite);
  });

  test('should initialize with correct values', () => {
    expect(game.width).toBe(200);
    expect(game.height).toBe(200);
    expect(game.id).toBe(1);
  });

  test('.update should call .update on sprite', () => {
    const deltaTime = 16;
    game.update(deltaTime);
    expect(game.sprite.update).toHaveBeenCalledWith(deltaTime);
  });

  test('.draw should call .draw on sprite', () => {
    game.sprite.draw = jest.fn();
    game.draw(mockContext);
    expect(game.sprite.draw).toHaveBeenCalledWith(mockContext);
  });
});

