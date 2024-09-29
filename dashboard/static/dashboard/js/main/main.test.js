import { Game } from './main.js';
import { UserInterface } from '../userInterface/userInterface.js';
import { Sprite } from '../sprite/sprite.js';
import { ChartClass } from '../chart/chart.js';

// Mock dependencies
jest.mock('../sprite/sprite.js');
jest.mock('../chart/chart.js');

// Mock global fetch function
global.fetch = jest.fn(() =>
  Promise.resolve({
    json: () => Promise.resolve({
      satiation: 75,
      current_state: 'RUNNING'
    })
  })
);

describe('Game class', () => {
  let game, mockContext;

  beforeEach(() => {
    jest.useFakeTimers();
    game = new Game(200, 200, 1, "husky/one");
    mockContext = {
      drawImage: jest.fn(),
      fillText: jest.fn(),
      fillRect: jest.fn(),
    };
  });

  afterEach(() => {
    jest.clearAllTimers();
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
    expect(game.chartObj).toBeInstanceOf(ChartClass);
  });

  test('should initialize with correct values', () => {
    expect(game.width).toBe(200);
    expect(game.height).toBe(200);
    expect(game.id).toBe(1);
    expect(game.url).toBe("husky/one");
  });

  test('.fetchStatus should update status', async () => {
    await game.fetchStatus();
    expect(fetch).toHaveBeenCalledWith('/dashboard/sprite/1/update-status/');
    expect(game.satiation).toBe(75);
    expect(game.sprite.setState).toHaveBeenCalledWith('RUNNING');
    expect(game.chartObj.updateChart).toHaveBeenCalledWith({
      satiation: 75,
      current_state: 'RUNNING'
    });
  });

  test('should call fetchStatus every 61 seconds', () => {
    const mockFetchStatus = jest.spyOn(game, 'fetchStatus');
    expect(mockFetchStatus).not.toHaveBeenCalled();
    jest.advanceTimersByTime(30000);
    expect(mockFetchStatus).not.toHaveBeenCalled();
    jest.advanceTimersByTime(31000);
    expect(mockFetchStatus).toHaveBeenCalledTimes(1);
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

