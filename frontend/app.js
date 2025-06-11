(async function () {
  async function fetchToken() {
    const res = await fetch('/api/chat/directline/token');
    const data = await res.json();
    return data.token;
  }

  let token = await fetchToken();
  const directLine = window.WebChat.createDirectLine({
    token,
    domain: '/api/chat/directline'
  });

  // Auto-refresh token every 25 minutes
  setInterval(async () => {
    token = await fetchToken();
    directLine.reconnect({ token });
  }, 25 * 60 * 1000);

  window.WebChat.renderWebChat({ directLine }, document.getElementById('webchat'));
})();
