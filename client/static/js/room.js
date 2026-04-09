// =========================
// SOCKET
// =========================
const socket = io({
  transports: ["polling"],
  timeout: 20000,
});

const roomId = localStorage.getItem("room_id");

const token = localStorage.getItem("token");
const payload = JSON.parse(atob(token.split(".")[1]));
const currentUser = payload.username;

// =========================
// ENTRAR NA SALA
// =========================
socket.on("connect", () => {
  console.log("🟢 Connected to socket");

  socket.emit("join_room", {
    room_id: roomId,
    username: currentUser,
  });
});

// =========================
// EVENTOS
// =========================

// jogador entrou
socket.on("player_joined", () => {
  loadRoomState();
});

// jogo começou
socket.on("game_started", () => {
  window.location.href = "/game";
});

// =========================
// CARREGAR ESTADO
// =========================
async function loadRoomState() {
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
}

// =========================
// START GAME (SOCKET)
// =========================
function startGame() {
  socket.emit("start_game", {
    room_id: roomId,
    player: currentUser,
  });
}

// =========================
// INIT
// =========================
window.onload = loadRoomState;

// =========================
// EXPORT
// =========================
window.startGame = startGame;
