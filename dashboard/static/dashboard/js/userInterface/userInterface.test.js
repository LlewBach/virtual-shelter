import { UserInterface } from "./userInterface";

describe('UserInterface class', () => {
  let game, mockContext, userInterface;

  beforeEach(() => {
    game = {
      satiation: 75
    }
    mockContext = {
      fillText: jest.fn(),
      fillRect: jest.fn(),
    }
    userInterface = new UserInterface(game);
  });

  test('should create an instance of UserInterface', () => {
    expect(userInterface).toBeInstanceOf(UserInterface);
  });

  test('should contain necessary keys', () => {
    expect(userInterface).toHaveProperty('game');
  });

  test('.draw method should call context methods correctly', () => {
    userInterface.draw(mockContext);
    expect(mockContext.fillText).toHaveBeenCalledWith('Satiation: 75', 5, 15);
    expect(mockContext.fillRect).toHaveBeenCalledWith(65, 8, 75, 6);
  });
});