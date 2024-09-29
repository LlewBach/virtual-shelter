import { feedSprite, getCSRFToken } from "./button1.js";

// Mock global fetch function
global.fetch = jest.fn(() =>
  Promise.resolve({
    json: () => Promise.resolve({
      success: true,
      tokens: 10
    }),
  })
);

// Mock document.cookie for CSRF token handling
Object.defineProperty(document, 'cookie', {
  writable: true,
  value: 'csrftoken=mockedToken',
});

document.querySelector = jest.fn().mockImplementation((selector) => {
  if (selector === '#token-count') {
    return { textContent: '' };
  }
});


describe('feedSprite', () => {
  beforeEach(() => {
    fetch.mockClear();
    // Mock the token count element in the DOM
    const tokenCountElement = { textContent: '5' };
    document.querySelector.mockReturnValue(tokenCountElement);
  });

  test('should call fetch with the correct URL and headers', async () => {
    const spriteId = 1;
    await feedSprite(spriteId);
    expect(fetch).toHaveBeenCalledTimes(1);
    expect(fetch).toHaveBeenCalledWith(`/dashboard/sprite/${spriteId}/feed/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': 'mockedToken',
      },
    });
  });

  test('getCSRFToken should extract the token from document.cookie', () => {
    const csrfToken = getCSRFToken();
    expect(csrfToken).toBe('mockedToken');
  });

  test('should call updateTokenCount when response is successful', async () => {
    // Mock the token count element in the DOM
    const tokenCountElement = { textContent: '5' };
    document.querySelector.mockReturnValue(tokenCountElement);

    const response = await feedSprite(1);

    expect(response.success).toBe(true);
    expect(response.tokens).toBe(10);
    expect(tokenCountElement.textContent).toBe('10');
  });

  test('should not update token count when response is unsuccessful', async () => {
    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        json: () => Promise.resolve({ success: false }),
      })
    );
    // Mock the token count element in the DOM
    const tokenCountElement = { textContent: '5' };
    document.querySelector.mockReturnValue(tokenCountElement);

    const response = await feedSprite(1);
    expect(response.success).toBe(false);
    expect(document.querySelector('#token-count').textContent).toBe('5');
  });
});
