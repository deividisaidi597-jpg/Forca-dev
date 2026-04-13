// =========================
// USER + ROOM
// =========================
const roomId = localStorage.getItem("room_id");

const token = localStorage.getItem("token");
const payload = JSON.parse(atob(token.split(".")[1]));
const currentUser = payload.username;

// =========================
// CARREGAR ESTADO DA SALA
// =========================
async function loadRoomState() {
  try {
    const { data } = await apiRequest(`/game/${roomId}`);

    document.getElementById("room-code").innerText = "Room: " + data.room_id;

    const playersDiv = document.getElementById("players");
    playersDiv.innerHTML = "";

    data.players.forEach((player) => {
      const p = document.createElement("p");

      const score = data.score?.[player] ?? 0;

      if (player === data.owner) {
        p.innerText = `👑 ${player} (${score} pts)`;
      } else {
        p.innerText = `👤 ${player} (${score} pts)`;
      }

      if (player === currentUser) {
        p.style.fontWeight = "bold";
      }

      playersDiv.appendChild(p);
    });

    const startButton = document.getElementById("start-btn");

    if (startButton) {
      startButton.disabled = currentUser !== data.owner;
    }

    // 👉 se jogo começou, redireciona automaticamente
    if (data.game_status !== "WAITING") {
      window.location.href = "/game";
    }
  } catch (err) {
    console.error("Erro ao carregar sala:", err);
  }
}

// =========================
// START GAME (HTTP)
// =========================
async function startGame() {
  try {
    await apiRequest("/game/start", "POST", { room_id: roomId }, true);
  } catch (err) {
    console.error("Erro ao iniciar jogo:", err);
  }
}

// =========================
// POLLING (ATUALIZA A SALA)
// =========================
setInterval(loadRoomState, 2000);

// =========================
// INIT
// =========================
window.onload = loadRoomState;

// =========================
// EXPORT
// =========================
window.startGame = startGame;
