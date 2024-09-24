export function feedSprite(spriteId) {
  fetch(`/dashboard/sprite/${spriteId}/feed/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCSRFToken(),
      // 'Content-Type': 'application/json'
    },
  })
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

