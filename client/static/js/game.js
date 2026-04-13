// =========================
// USER + ROOM
// =========================
const roomId = localStorage.getItem("room_id");

const token = localStorage.getItem("token");
const payload = JSON.parse(atob(token.split(".")[1]));
const currentUser = payload.username;

let gameOwner = null;

// =========================
// AÇÕES DO JOGADOR
// =========================
async function guessLetter() {
  const letter = document.getElementById("letter").value;

  if (!letter) {
    showMessage("Type a letter!", "orange");
    return;
  }

  try {
    const { data } = await apiRequest(
      "/game/guess-letter",
      "POST",
      {
        room_id: roomId,
        letter: letter,
      },
      true,
    );

    updateGameUI(data);

    if (data.message) {
      showMessage(data.message, "green");
    }

    document.getElementById("letter").value = "";
  } catch (err) {
    console.error(err);
    showMessage("Error guessing letter", "red");
  }
}

async function guessWord() {
  const word = document.getElementById("word-input").value;

  if (!word) {
    showMessage("Type a word!", "orange");
    return;
  }

  try {
    const { data } = await apiRequest(
      "/game/guess-word",
      "POST",
      {
        room_id: roomId,
        word: word,
      },
      true,
    );

    updateGameUI(data);

    if (data.message) {
      showMessage(data.message, "green");
    }

    document.getElementById("word-input").value = "";
  } catch (err) {
    console.error(err);
    showMessage("Error guessing word", "red");
  }
}

async function restartGame() {
  try {
    const { data } = await apiRequest(
      "/game/restart",
      "POST",
      {
        room_id: roomId,
      },
      true,
    );

    updateGameUI(data);

    if (data.message) {
      showMessage(data.message, "green");
    }
  } catch (err) {
    console.error(err);
  }
}

async function changeCategory() {
  const select = document.getElementById("category-select");
  const category = select.value;
  const modal = document.getElementById("category-selector");

  if (!category) {
    showMessage("Select a category!", "red");
    return;
  }

  try {
    const { data } = await apiRequest(
      "/game/change-category",
      "POST",
      {
        room_id: roomId,
        category: category,
      },
      true,
    );

    updateGameUI(data);

    if (modal) modal.style.display = "none";

    showMessage("Category changed!", "green");
  } catch (err) {
    console.error(err);
  }
}

// =========================
// POLLING DO JOGO
// =========================
setInterval(async () => {
  try {
    const { data } = await apiRequest(`/game/${roomId}`, "GET", null, true);
    updateGameUI(data);
  } catch (err) {
    console.error("Erro ao atualizar jogo:", err);
  }
}, 2000);

// =========================
// ATUALIZAR UI
// =========================
function updateGameUI(data) {
  if (data.owner) {
    gameOwner = data.owner;
  }

  const restartBtn = document.getElementById("restart-btn");

  if (restartBtn) {
    restartBtn.disabled = true;
  }

  // Palavra
  if (data.correct_word) {
    document.getElementById("word").innerText = formatWord(data.correct_word);
  } else if (data.masked_word) {
    document.getElementById("word").innerText = data.masked_word;
  }

  // Tamanho
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
// INIT
// =========================
async function loadInitialGame() {
  try {
    const { data } = await apiRequest(`/game/${roomId}`);
    updateGameUI(data);
  } catch (err) {
    console.error(err);
  }
}
function closeCategorySelector() {
  const modal = document.getElementById("category-selector");
  if (modal) modal.style.display = "none";
}

window.onload = loadInitialGame;

// =========================
// EXPORT
// =========================
window.guessLetter = guessLetter;
window.guessWord = guessWord;
window.restartGame = restartGame;
window.changeCategory = changeCategory;
window.closeCategorySelector = closeCategorySelector;
