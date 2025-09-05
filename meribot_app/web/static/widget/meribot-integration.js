// Widget MeriBot básico
(function() {
  const widget = document.createElement('div');
  widget.className = 'widget-meribot';
  widget.innerHTML = `
    <div class="widget-meribot-header">MeriBot</div>
    <div class="widget-meribot-body" id="meribot-body">¡Hola! ¿En qué puedo ayudarte?</div>
    <form class="widget-meribot-input" id="meribot-form">
      <input type="text" id="meribot-input" placeholder="Escribe tu mensaje..." autocomplete="off" />
      <button type="submit">Enviar</button>
    </form>
  `;
  document.body.appendChild(widget);

  const form = document.getElementById('meribot-form');
  const input = document.getElementById('meribot-input');
  const body = document.getElementById('meribot-body');

  form.addEventListener('submit', function(e) {
    e.preventDefault();
    const msg = input.value.trim();
    if (msg) {
      body.innerHTML += `<div><strong>Tú:</strong> ${msg}</div>`;
      input.value = '';
      // Aquí puedes llamar a la API del chatbot
      setTimeout(() => {
        body.innerHTML += `<div><strong>MeriBot:</strong> (respuesta simulada)</div>`;
      }, 800);
    }
  });
})();
