import { feedSprite, getCSRFToken } from "./button1.js";

// Mock global fetch function
global.fetch = jest.fn(() =>
  Promise.resolve({
    json: () => Promise.resolve({}),
  })
);

// Mock document.cookie for CSRF token handling
Object.defineProperty(document, 'cookie', {
  writable: true,
  value: 'csrftoken=mockedToken',
});


describe('feedSprite', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test('should call fetch with the correct URL and headers', () => {
    const spriteId = 1;
    feedSprite(spriteId);
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
});
