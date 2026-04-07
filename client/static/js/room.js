async function loadRoom() {
  const roomId = localStorage.getItem("room_id");
  const token = localStorage.getItem("token");

  const payload = JSON.parse(atob(token.split(".")[1]));
  const currentUser = payload.username;

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

  const startButton = document.querySelector("button");

  if (currentUser !== data.owner) {
    startButton.style.display = "none";
  }

  setTimeout(loadRoom, 10000);
}

async function startGame() {
  const roomId = localStorage.getItem("room_id");

  const { response, data } = await apiRequest(
    "/game/start",
    "POST",
    { room_id: roomId },
    true,
  );

  if (response.ok) {
    showMessage("Game started!", "green");

    setTimeout(() => {
      window.location.href = "/game";
    }, 1000);
  } else {
    showMessage(data.message, "red");
  }
}

window.loadRoom = loadRoom;
window.startGame = startGame;
