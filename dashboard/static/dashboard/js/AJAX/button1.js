export async function feedSprite(spriteId) {
  const response = await fetch(`/dashboard/sprite/${spriteId}/feed/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCSRFToken(),
      // 'Content-Type': 'application/json'
    },
  });

  const data = await response.json();
  return data;
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

