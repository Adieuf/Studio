(async function () {
  async function startConversation() {
    const res = await fetch('/api/chat/conversations', { method: 'POST' });
    return res.json();
  }

  let { token, conversationId } = await startConversation();
  let watermark = sessionStorage.getItem('watermark');

  let directLine = window.WebChat.createDirectLine({
    domain: '/api/chat',
    token,
    conversationId,
  });

  window.WebChat.renderWebChat({ directLine }, document.getElementById('webchat'));

  directLine.connectionStatus$.subscribe(async status => {
    if (status === 4 || status === 5) {
      ({ token, conversationId } = await startConversation());
      directLine = window.WebChat.createDirectLine({
        domain: '/api/chat',
        token,
        conversationId,
      });
      window.WebChat.renderWebChat(
        { directLine, watermark },
        document.getElementById('webchat')
      );
    }
  });

  directLine.activity$.subscribe(activity => {
    if (activity.id) {
      watermark = activity.id;
      sessionStorage.setItem('watermark', watermark);
    }
  });
})();
