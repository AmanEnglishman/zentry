(function () {
  const config = window.ZENTRY_CHAT;
  if (!config || !config.token) {
    return;
  }

  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
  const socket = new WebSocket(
    `${protocol}://${window.location.host}/ws/chat/${config.conversationId}/?token=${config.token}`
  );
  const form = document.getElementById('message-form');
  const input = form ? form.querySelector('input[name="content"]') : null;
  const list = document.getElementById('message-list');
  const typingStatus = document.getElementById('typing-status');
  let typingTimer = null;

  function appendMessage(message) {
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    if (String(message.sender.id) === String(config.currentUserId)) {
      bubble.classList.add('mine');
    }

    const text = document.createElement('p');
    text.textContent = message.content;

    const meta = document.createElement('span');
    meta.textContent = new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    bubble.appendChild(text);
    bubble.appendChild(meta);
    list.appendChild(bubble);
    list.scrollTop = list.scrollHeight;
  }

  socket.addEventListener('open', function () {
    socket.send(JSON.stringify({ type: 'read' }));
  });

  socket.addEventListener('message', function (event) {
    const data = JSON.parse(event.data);
    if (data.type === 'message') {
      appendMessage(data);
      socket.send(JSON.stringify({ type: 'read' }));
    }
    if (data.type === 'typing' && String(data.user_id) !== String(config.currentUserId)) {
      typingStatus.textContent = data.is_typing ? 'Typing...' : 'Realtime chat';
    }
  });

  if (form && input) {
    form.addEventListener('submit', function (event) {
      if (socket.readyState !== WebSocket.OPEN) {
        return;
      }
      event.preventDefault();
      const content = input.value.trim();
      if (!content) {
        return;
      }
      socket.send(JSON.stringify({ type: 'message', content: content }));
      input.value = '';
      socket.send(JSON.stringify({ type: 'typing', is_typing: false }));
    });

    input.addEventListener('input', function () {
      if (socket.readyState !== WebSocket.OPEN) {
        return;
      }
      socket.send(JSON.stringify({ type: 'typing', is_typing: true }));
      clearTimeout(typingTimer);
      typingTimer = setTimeout(function () {
        socket.send(JSON.stringify({ type: 'typing', is_typing: false }));
      }, 900);
    });
  }
})();
