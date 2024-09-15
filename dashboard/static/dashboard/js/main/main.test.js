import { Game } from './main.js';
import { UserInterface } from '../userInterface/userInterface.js';
import { Sprite } from '../sprite/sprite.js';

// Mock dependencies
jest.mock('../sprite/sprite.js');

// Mock global fetch function
global.fetch = jest.fn(() =>
  Promise.resolve({
    json: () => Promise.resolve({ satiation: 75 })
  })
);

describe('Game class', () => {
  let game, mockContext;

  beforeEach(() => {
    game = new Game(200, 200, 1, "husky/one");
    mockContext = {
      drawImage: jest.fn(),
      fillText: jest.fn(),
      fillRect: jest.fn(),
    };
  });

  test('should create an instance of Game', () => {
    expect(game).toBeInstanceOf(Game);
  });

  test('should contain necessary keys', () => {
    expect(game).toHaveProperty('width');
    expect(game).toHaveProperty('height');
    expect(game).toHaveProperty('id');
    expect(game).toHaveProperty('url');
    expect(game).toHaveProperty('satiation');
  });

  test('should initialize with class instances', () => {
    expect(game.userInterface).toBeInstanceOf(UserInterface);
    expect(game.sprite).toBeInstanceOf(Sprite);
  });

  test('should initialize with correct values', () => {
    expect(game.width).toBe(200);
    expect(game.height).toBe(200);
    expect(game.id).toBe(1);
    expect(game.url).toBe("husky/one");
    // expect(game.satiation).toBe(55);
  });

  test('.fetchStatus should update status', async () => {
    await game.fetchStatus();
    expect(fetch).toHaveBeenCalledWith('/dashboard/sprite/1/update-status/');
    expect(game.satiation).toBe(75);
  });

  test('.update should call .update on sprite', () => {
    const deltaTime = 16;
    game.update(deltaTime);
    expect(game.sprite.update).toHaveBeenCalledWith(deltaTime);
  });

  test('.draw should call .draw on correct game properties', () => {
    game.userInterface.draw = jest.fn();
    game.sprite.draw = jest.fn();
    game.draw(mockContext);
    expect(game.userInterface.draw).toHaveBeenCalledWith(mockContext);
    expect(game.sprite.draw).toHaveBeenCalledWith(mockContext);
  });
});

