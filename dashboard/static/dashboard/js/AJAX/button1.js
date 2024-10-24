export async function feedSprite(spriteId) {
  try {
    const response = await fetch(`/dashboard/sprite/${spriteId}/feed/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCSRFToken(),
      },
    });

    const data = await response.json();
    if (data.success) {
      updateTokenCount(data.tokens);
    }
    return data;
  } catch (error) {
    console.error('Failed to feed sprite:', error);
    return { success: false, error: 'An error occurred while feeding the sprite.' };
  }
}


export function getCSRFToken() {
  const cookies = document.cookie.split(';');
  for (let cookie of cookies) {
    cookie = cookie.trim();
    if (cookie.startsWith('csrftoken=')) {
      return cookie.substring('csrftoken='.length);
    }
  }
  return null;
}


function updateTokenCount(newTokenCount) {
  const tokenCountElement = document.querySelector('#token-count');
  tokenCountElement.textContent = `${newTokenCount}`;
}

