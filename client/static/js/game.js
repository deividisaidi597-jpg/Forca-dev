// =========================
// SOCKET
// =========================
const socket = io({
  transports: ["polling"],
  timeout: 20000,
});

// =========================
// USER + ROOM
// =========================
const roomId = localStorage.getItem("room_id");

const token = localStorage.getItem("token");
const payload = JSON.parse(atob(token.split(".")[1]));
const currentUser = payload.username;
let gameOwner = null;
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
// AÇÕES DO JOGADOR
// =========================
function guessLetter() {
  const letter = document.getElementById("letter").value;

  if (!letter) {
    showMessage("Type a letter!", "orange");
    return;
  }

  socket.emit("guess_letter", {
    room_id: roomId,
    player: currentUser,
    letter: letter,
  });

  document.getElementById("letter").value = "";
}

function guessWord() {
  const word = document.getElementById("word-input").value;

  if (!word) {
    showMessage("Type a word!", "orange");
    return;
  }

  socket.emit("guess_word", {
    room_id: roomId,
    player: currentUser,
    word: word,
  });

  document.getElementById("word-input").value = "";
}

function startGame() {
  socket.emit("start_game", {
    room_id: roomId,
    player: currentUser,
  });
}

function restartGame() {
  socket.emit("restart_game", {
    room_id: roomId,
    player: currentUser,
  });
}

function changeCategory() {
  const select = document.getElementById("category-select");
  const category = select.value;
  const modal = document.getElementById("category-selector");

  if (!category) {
    showMessage("Select a category!", "red");
    return;
  }

  socket.emit("change_category", {
    room_id: roomId,
    player: currentUser,
    category: category,
  });

  if (modal) modal.style.display = "none";

  showMessage("Changing category...", "green");
}

// =========================
// RECEBER ATUALIZAÇÕES
// =========================

// jogador entrou
socket.on("player_joined", (data) => {
  showMessage(data.message, "green");
});

// jogo começou
socket.on("game_started", (data) => {
  updateGameUI(data);
  showMessage("Game started!", "green");
});

// atualização do jogo
socket.on("game_update", (data) => {
  updateGameUI(data);
  console.log("UPDATE", data);
  if (data.message) {
    showMessage(data.message, "green");
  }
});

socket.on("private_message", (data) => {
  if (data.message) {
    showMessage(data.message, "red");
  }
});

// nova rodada
socket.on("round_restart", (data) => {
  const modal = document.getElementById("category-selector");

  if (data.finished_category) {
    if (currentUser !== gameOwner) {
      showMessage("Waiting for owner to choose category...", "orange");
      return;
    }

    showCategorySelector(data.categories);
    return;
  }
  if (modal) modal.style.display = "none";

  updateGameUI(data);
  showMessage("New round!", "green");
});

// categoria mudou
socket.on("category_changed", (data) => {
  updateGameUI(data);
  showMessage("Category changed!", "green");
});

// =========================
// ATUALIZAR UI
// =========================
function updateGameUI(data) {
  if (data.owner) {
    gameOwner = data.owner;
  }
  const restartBtn = document.getElementById("restart-btn");

  // sempre começa desabilitado
  if (restartBtn) {
    restartBtn.disabled = true;
  }

  // Palavra
  if (data.correct_word) {
    document.getElementById("word").innerText = formatWord(data.correct_word);
  } else if (data.masked_word) {
    document.getElementById("word").innerText = data.masked_word;
  }

  // Tamanho da palavra
  if (data.word_length) {
    document.getElementById("word-length").innerText =
      "Letters: " + data.word_length;
  }

  // Categoria
  if (data.category) {
    document.getElementById("category").innerText =
      "Category: " + data.category;
  }

  // Jogadores
  renderPlayers(
    data.players,
    data.player_errors || {},
    data.score || {},
    data.current_player || null,
  );

  // Forca
  const errors = data.player_errors?.[currentUser] ?? 0;
  drawHangman(errors);

  const isRoundFinished = data.game_status === "ROUND_FINISHED";
  const isOwner = currentUser === gameOwner;

  if (isRoundFinished) {
    showMessage("Round finished!", "orange");

    if (restartBtn) {
      restartBtn.disabled = !isOwner;
    }

    return;
  }
}

// =========================
// UI HELPERS
// =========================
function drawHangman(errors) {
  const stages = [
    "",
    " O ",
    " O \n | ",
    " O \n/| ",
    " O \n/|\\",
    " O \n/|\\\n/ ",
    " O \n/|\\\n/ \\",
  ];

  document.getElementById("hangman").innerText = stages[errors];
}

function renderPlayers(players, errors, score, currentPlayer) {
  const container = document.getElementById("players");
  container.innerHTML = "";

  if (!players) return;

  players.forEach((player) => {
    const el = document.createElement("p");

    const err = errors?.[player] ?? 0;
    const pts = score?.[player] ?? 0;

    el.innerText = `🧍 ${player} | ❌ ${err} | ⭐ ${pts}`;
    if (player === currentPlayer) {
      el.style.color = "yellow";
      el.style.fontWeight = "bold";
    }

    container.appendChild(el);
  });
}

function formatWord(word) {
  return word
    .split("")
    .map((c) => (c === " " ? "␣" : c))
    .join(" ");
}

// =========================
// CATEGORIAS
// =========================
function showCategorySelector(categories) {
  const container = document.getElementById("category-selector");
  const select = document.getElementById("category-select");

  if (currentUser !== gameOwner) {
    select.disabled = true;
  }

  container.style.display = "block";
  select.innerHTML = "";

  categories
    .filter((c) => c.remaining > 0)
    .forEach((cat) => {
      const option = document.createElement("option");
      option.value = cat.category;
      option.textContent = `${cat.category} (${cat.remaining})`;
      select.appendChild(option);
    });
}

async function loadInitialGame() {
  const { data } = await apiRequest(`/game/${roomId}`);

  console.log("INIT GAME:", data);

  if (data.game_status === "ROUND_FINISHED") {
    const restartBtn = document.getElementById("restart-btn");

    if (restartBtn && currentUser === data.owner) {
      restartBtn.disabled = false;
    }
  }

  updateGameUI(data);

  // TRATAR ESTADO APÓS RELOAD
  const restartBtn = document.getElementById("restart-btn");

  if (restartBtn) {
    restartBtn.disabled = true;
  }

  if (data.game_status === "ROUND_FINISHED") {
    if (currentUser === data.owner) {
      restartBtn.disabled = false;
    } else {
      restartBtn.disabled = true;
      showMessage("Waiting for owner to start next round...", "orange");
    }
  }

  if (data.game_status === "FINISHED") {
    showMessage("🏁 Game finished!", "green");
    restartBtn.disabled = true;
  }
}

// =========================
// EXPORT
// =========================
window.onload = loadInitialGame;
window.guessLetter = guessLetter;
window.guessWord = guessWord;
window.startGame = startGame;
window.restartGame = restartGame;
window.changeCategory = changeCategory;
