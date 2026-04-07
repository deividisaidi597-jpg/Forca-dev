function loadDashboard() {
  const token = localStorage.getItem("token");

  if (!token) {
    window.location.href = "/";
    return;
  }

  const payload = JSON.parse(atob(token.split(".")[1]));
  document.getElementById("welcome").innerText = "Player: " + payload.username;
}

async function loadCategories() {
  const { data } = await apiRequest("/categories");

  const select = document.getElementById("category");

  data.categories.forEach((cat) => {
    const option = document.createElement("option");
    option.value = cat;
    option.innerText = cat;
    select.appendChild(option);
  });
}

async function loadGames() {
  const { data } = await apiRequest("/games");

  const container = document.getElementById("games-list");
  container.innerHTML = "";

  const token = localStorage.getItem("token");
  const payload = JSON.parse(atob(token.split(".")[1]));
  const currentUser = payload.username;

  data.games.forEach((game) => {
    let statusText = "";
    let color = "";

    if (game.status === "WAITING") {
      statusText = "🟡 WAITING";
      color = "orange";
    } else if (game.status === "IN_PROGRESS") {
      statusText = "⏳ IN_PROGRESS";
      color = "green";
    } else if (game.status === "ROUND_FINISHED") {
      statusText = "⌛ ROUND_FINISHED";
      color = "orange";
    } else if (game.status === "FINISHED") {
      statusText = "🏁 FINISHED";
      color = "gray";
    }

    const isPlayer = game.players.includes(currentUser);
    const isLocked = game.status === "IN_PROGRESS" && !isPlayer;
    const isFull = game.players.length >= 2 && !isPlayer;

    let button = "";

    if (isLocked) {
      button = `<button disabled>🔒 At stake</button>`;
    } else if (isFull) {
      button = `<button disabled>🚫 Full room</button>`;
    } else if (isPlayer) {
      button = `<button onclick="reconnectRoom('${game.room_id}')">🔁 Reconnect</button>`;
    } else {
      button = `<button onclick="enterRoom('${game.room_id}')">To enter</button>`;
    }

    const div = document.createElement("div");

    div.innerHTML = `
      <p>
        Room: ${game.room_id} <br>
        Status: <span style="color:${color}">${statusText}</span> <br>
        Players: ${game.players.join(", ")}
      </p>
      ${button}
      <hr>
    `;

    container.appendChild(div);
  });

  setTimeout(loadGames, 10000);
}

async function createGame() {
  const category = document.getElementById("category").value;

  const { response, data } = await apiRequest(
    "/game/create",
    "POST",
    { category },
    true,
  );

  if (response.ok) {
    localStorage.setItem("room_id", data.room_id);
    window.location.href = "/room";
  } else {
    showMessage(data.message, "red", "game-message");
  }
}

async function joinGame() {
  const roomId = document.getElementById("room_id").value;

  const { response, data } = await apiRequest(
    "/game/join",
    "POST",
    { room_id: roomId },
    true,
  );

  if (response.ok) {
    localStorage.setItem("room_id", roomId);
    showMessage("He entered the room!", "green", "game-message");

    setTimeout(() => {
      window.location.href = "/room";
    }, 1500);
    renderPlayers(data.players, data.player_errors, data.score);
  } else {
    showMessage(data.message, "red", "game-message");
  }
}

function reconnectRoom(roomId) {
  localStorage.setItem("room_id", roomId);
  window.location.href = "/room";
}

async function enterRoom(roomId) {
  const { response, data } = await apiRequest(
    "/game/join",
    "POST",
    { room_id: roomId },
    true,
  );

  if (response.ok) {
    localStorage.setItem("room_id", roomId);
    window.location.href = "/room";
  } else {
    showMessage(data.message, "red", "game-message");
  }
}

window.loadDashboard = loadDashboard;
window.loadCategories = loadCategories;
window.loadGames = loadGames;
window.createGame = createGame;
window.joinGame = joinGame;
window.reconnectRoom = reconnectRoom;
window.enterRoom = enterRoom;
