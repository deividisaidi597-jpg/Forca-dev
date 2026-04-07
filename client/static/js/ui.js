function showMessage(text, color) {
  const el = document.getElementById("message");
  if (!el) return;

  el.innerText = text;
  el.style.color = color;
}
function showEndRound(message) {
  const el = document.getElementById("message");

  el.innerHTML = `
    <div style="
      background: #222;
      padding: 15px;
      border-radius: 10px;
      color: #0f0;
      font-weight: bold;
      text-align: center;
      font-size: 18px;
      margin-top: 10px;
    ">
      🎉 ${message}
    </div>
  `;
}

window.showMessage = showMessage;
window.showEndRound = showEndRound;
