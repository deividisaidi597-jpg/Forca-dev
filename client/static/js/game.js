let selectedCategory = null;

// Remover ou modificar a função setInputsDisabled se não for mais necessária
// Ou mantê-la apenas para casos específicos como categoria finalizada
function setInputsDisabled(disabled) {
  // Esta função agora só é usada quando a categoria acaba
  console.log(
    "🔧 setInputsDisabled(",
    disabled,
    ") - Apenas para categoria finalizada",
  );
  document.getElementById("letter").disabled = disabled;
  document.getElementById("word-input").disabled = disabled;

  // Não desabilita os botões de chutar
  // Apenas os inputs
}

async function guessLetter() {
  const letter = document.getElementById("letter").value;

  if (!letter) {
    showMessage("Type a letter!", "orange");
    return;
  }

  const roomId = localStorage.getItem("room_id");

  const { response, data } = await apiRequest(
    "/game/guess",
    "POST",
    { room_id: roomId, letter },
    true,
  );
  console.log("💾 guessLetter - dados recebidos:", data);

  if (response.ok) {
    const token = localStorage.getItem("token");
    const payload = JSON.parse(atob(token.split(".")[1]));
    const currentUser = payload.username;

    if (
      data.player_status &&
      data.player_status[currentUser] === "ELIMINATED"
    ) {
      showMessage("You have been eliminated!", "red");
      return;
    }

    // ATUALIZA A PALAVRA
    if (data.correct_word) {
      const formattedWord = data.correct_word
        .split("")
        .map((char) => (char === " " ? "␣" : char))
        .join(" ");
      document.getElementById("word").innerText = formattedWord;
      console.log("Mostrando palavra completa:", formattedWord);
    } else if (data.masked_word) {
      document.getElementById("word").innerText = data.masked_word;
    }

    // Atualiza a forca e jogadores
    const errors =
      data.player_errors?.[data.last_player || data.current_player] ?? 0;
    drawHangman(errors);
    renderPlayers(data.players, data.player_errors, data.score);

    // VERIFICA SE A RODADA TERMINOU
    if (data.game_status === "ROUND_FINISHED") {
      // Apenas habilita o botão de próxima rodada
      const restartBtn = document.getElementById("restart-btn");
      if (restartBtn) restartBtn.disabled = false;

      showMessage("🎉 Full word! Click 'Next round' to continue.", "green");

      // NÃO mostra o modal aqui! Deixa para o restartGame
    } else {
      showMessage("Move made!", "green");
    }

    document.getElementById("letter").value = "";
  } else {
    showMessage(data.message, "red");
  }
}

// Modificar guessWord - REMOVER a verificação de categoria acabada
async function guessWord() {
  const word = document.getElementById("word-input").value;

  if (!word) {
    showMessage("Type a word!", "orange");
    return;
  }

  const roomId = localStorage.getItem("room_id");

  const { response, data } = await apiRequest(
    "/game/guess-word",
    "POST",
    { room_id: roomId, word },
    true,
  );

  if (response.ok) {
    const token = localStorage.getItem("token");
    const payload = JSON.parse(atob(token.split(".")[1]));
    const currentUser = payload.username;

    if (
      data.player_status &&
      data.player_status[currentUser] === "ELIMINATED"
    ) {
      showMessage("You have been eliminated!", "red");
      return;
    }

    // ATUALIZA A PALAVRA
    if (data.correct_word) {
      const formattedWord = data.correct_word
        .split("")
        .map((char) => (char === " " ? "␣" : char))
        .join(" ");
      document.getElementById("word").innerText = formattedWord;
      console.log("Mostrando palavra completa:", formattedWord);
    } else if (data.masked_word) {
      document.getElementById("word").innerText = data.masked_word;
    }

    const errors =
      data.player_errors?.[data.last_player || data.current_player] ?? 0;
    drawHangman(errors);
    renderPlayers(data.players, data.player_errors, data.score);

    // Verifica se a rodada terminou
    if (data.game_status === "ROUND_FINISHED") {
      const restartBtn = document.getElementById("restart-btn");
      if (restartBtn) restartBtn.disabled = false;

      showMessage(
        "🎉 You guessed the word correctly! Click 'Next round' to continue.",
        "green",
      );

      // NÃO mostra o modal aqui! Deixa para o restartGame
    } else {
      showMessage("❌ Incorrect word!", "red");
    }

    document.getElementById("word-input").value = "";
  } else {
    showMessage(data.message, "red");
  }
}

// Modificar loadGame - NÃO mostrar modal automaticamente
async function loadGame() {
  const roomId = localStorage.getItem("room_id");
  if (!roomId) {
    window.location.href = "/";
    return;
  }

  const { response, data } = await apiRequest(
    `/game/${roomId}`,
    "GET",
    null,
    true,
  );
  console.log("💾 loadGame - dados do backend:", data);

  if (!response.ok) {
    if (response.status === 404) {
      localStorage.removeItem("room_id");
      window.location.href = "/";
    }
    return;
  }

  // PEGAR O CURRENT USER DO TOKEN
  const token = localStorage.getItem("token");
  let currentUser = null;
  if (token) {
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      currentUser = payload.username;
    } catch (e) {
      console.error("Error decoding token", e);
    }
  }

  // Atualiza informações básicas
  document.getElementById("category").innerText =
    "Category: " + (data.category || "Indefinida");
  document.getElementById("word-length").innerText =
    "Letter: " + (data.secret_word?.length || 0);

  // Mostra a palavra (mascarada ou completa)
  let displayWord = "";
  let isWordComplete = false;

  if (data.status === "ROUND_FINISHED") {
    // Mostra a palavra completa com espaços entre letras
    displayWord = data.secret_word
      .split("")
      .map((char) => (char === " " ? "␣" : char))
      .join(" ");
    isWordComplete = true;
    const restartBtn = document.getElementById("restart-btn");
    if (restartBtn) restartBtn.disabled = false;
  } else {
    // Mostra a palavra mascarada, preservando espaços
    displayWord = data.secret_word
      .split("")
      .map((char) => {
        if (char === " ") return "␣"; // Mostra símbolo para espaço
        if ((data.guessed_letters || []).includes(char)) return char;
        return "_";
      })
      .join(" "); // Espaço entre cada caractere

    isWordComplete = !displayWord.includes("_");
    const restartBtn = document.getElementById("restart-btn");
    if (restartBtn) restartBtn.disabled = !isWordComplete;
  }

  document.getElementById("word").innerText = displayWord;

  // SEMPRE manter inputs habilitados inicialmente
  document.getElementById("letter").disabled = false;
  document.getElementById("word-input").disabled = false;

  if (isWordComplete && data.status !== "ROUND_FINISHED") {
    showMessage("🎉 Full word! Click 'Next round' to continue.", "green");
  }

  // NÃO mostrar o modal automaticamente aqui!
  // O modal só deve ser mostrado quando o usuário clicar em "Próxima rodada"
  // e o backend retornar finished_category: true

  // SÓ USA currentUser SE ELE EXISTIR
  const errors = currentUser ? (data.player_errors?.[currentUser] ?? 0) : 0;
  drawHangman(errors);
  renderPlayers(data.players, data.player_errors, data.score);
}

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

function renderPlayers(players, errors, score) {
  const container = document.getElementById("players");
  container.innerHTML = "";

  if (!players) return;

  players.forEach((player) => {
    const el = document.createElement("p");

    const erros = errors[player] || 0;
    const pontos = score[player] || 0;

    el.innerText = `🧍 ${player} | ❌ ${erros} | ⭐ ${pontos}`;
    container.appendChild(el);
  });
}

// SÓ AQUI mostra o modal quando a categoria acabar
async function restartGame() {
  const roomId = localStorage.getItem("room_id");

  showMessage("Carregando próxima palavra...", "info");

  const { response, data } = await apiRequest(
    "/game/restart",
    "POST",
    { room_id: roomId },
    true,
  );

  if (!response.ok) {
    showMessage(data.message || "Error when restarting", "error");
    return;
  }

  // VERIFICA SE A CATEGORIA ACABOU
  if (data.finished_category) {
    console.log("🏆 Categoria finalizada! Mostrando modal...");
    const categoriesList = data.categories || [];

    if (categoriesList.length > 0) {
      // Mostra o modal apenas quando a categoria realmente acabou
      showCategorySelector(categoriesList);
      showMessage(
        `Category "${data.finished_category}" finished! Choose another.`,
        "green",
      );
      // Desabilita os inputs até escolher nova categoria
      document.getElementById("letter").disabled = true;
      document.getElementById("word-input").disabled = true;
      // Mantém o botão de próxima rodada desabilitado
      const restartBtn = document.getElementById("restart-btn");
      if (restartBtn) restartBtn.disabled = true;
    } else {
      showMessage(
        "Congratulations! All categories have been completed!",
        "green",
      );
    }
    return;
  }

  // Se chegou aqui, a categoria tem palavras, continua normalmente
  console.log("✅ restartGame - Nova palavra carregada");

  // Formata a palavra mascarada com espaços
  const formattedMaskedWord = data.masked_word;
  document.getElementById("word").innerText = formattedMaskedWord;
  document.getElementById("category").innerText = "Categoria: " + data.category;
  document.getElementById("word-length").innerText =
    "Letras: " + data.word_length;

  // Habilita os inputs
  document.getElementById("letter").disabled = false;
  document.getElementById("word-input").disabled = false;
  document.getElementById("letter").value = "";
  document.getElementById("word-input").value = "";

  // Desabilita o botão restart até a próxima rodada terminar
  const restartBtn = document.getElementById("restart-btn");
  if (restartBtn) restartBtn.disabled = true;

  // Reseta a forca
  drawHangman(0);

  // Atualiza jogadores
  renderPlayers(data.players, data.player_errors, data.score);

  // Garante que o modal está escondido
  const modal = document.getElementById("category-selector");
  if (modal) modal.style.display = "none";

  showMessage("New word! Keep playing.", "green");
}

function renderCategories(categories) {
  const el = document.getElementById("categories-status");
  el.innerHTML = "";

  categories.forEach((cat) => {
    const p = document.createElement("p");
    p.innerText = `${cat.category} (${cat.remaining}/${cat.total})`;
    el.appendChild(p);
  });
}

function showCategorySelector(categories) {
  const container = document.getElementById("category-selector");
  const select = document.getElementById("category-select");

  if (!container || !select) return;

  // Limpa o select
  select.innerHTML = '<option value="">📋 Selecione uma categoria</option>';

  // Filtra apenas categorias com remaining > 0
  const availableCategories = categories.filter((cat) => cat.remaining > 0);

  if (availableCategories.length === 0) {
    select.innerHTML = '<option value="">🎉 All categories completed!</option>';
    return;
  }

  // Popula com as categorias disponíveis (apenas as que têm palavras)
  availableCategories.forEach((cat) => {
    const option = document.createElement("option");
    option.value = cat.category;
    option.textContent = `${cat.category} (${cat.remaining} remaining words)`;
    select.appendChild(option);
  });

  // Seleciona a primeira opção automaticamente
  if (select.options.length > 1) {
    select.selectedIndex = 1;
    selectedCategory = select.options[1].value;
  }

  // ADICIONA O EVENT LISTENER PARA ATUALIZAR selectedCategory
  select.onchange = function () {
    selectedCategory = this.value;
  };

  container.style.display = "block";
}

function updateRestartButton(data) {
  const btn = document.querySelector("button[onclick='restartGame()']");
  if (!btn) return;

  // Ativa só se a rodada terminou
  btn.disabled =
    data.status !== "ROUND_FINISHED" &&
    !data.message?.includes("Finalized category");
}

function setInputsDisabled(disabled) {
  // Desabilita apenas os inputs de texto
  console.log("🔧 setInputsDisabled(", disabled, ")");
  console.log(
    "Inputs antes:",
    document.getElementById("letter").disabled,
    document.getElementById("word-input").disabled,
  );
  document.getElementById("letter").disabled = disabled;
  document.getElementById("word-input").disabled = disabled;

  // Desabilita/abilita os botões de chute (letter e word)
  const buttons = document.querySelectorAll("button");
  buttons.forEach((btn) => {
    // Mantém o botão de próxima rodada SEMPRE habilitado quando disabled=false
    // E NUNCA desabilita o botão de próxima rodada
    if (btn.id === "restart-btn") {
      // Não faz nada - mantém o estado atual
      return;
    }

    // Desabilita os outros botões (chutar letra, chutar palavra)
    // Mas NUNCA desabilita os botões do modal (Iniciar, Cancelar)
    const isModalButton =
      btn.parentElement?.parentElement?.id === "category-selector" ||
      btn.innerText === "Iniciar" ||
      btn.innerText === "Cancelar";

    if (!isModalButton) {
      btn.disabled = disabled;
    }
  });
  console.log(
    "Inputs depois:",
    document.getElementById("letter").disabled,
    document.getElementById("word-input").disabled,
  );
}

// Para habilitar inputs após escolher nova categoria
async function changeCategory() {
  const select = document.getElementById("category-select");
  const newCategory = select.value;

  if (!newCategory || newCategory === "") {
    showMessage("Select a category!", "error");
    return;
  }

  const roomId = localStorage.getItem("room_id");
  const token = localStorage.getItem("token");
  const payload = JSON.parse(atob(token.split(".")[1]));
  const currentPlayer = payload.username;

  showMessage("Changing category...", "green");

  const { response, data } = await apiRequest(
    "/game/change-category",
    "POST",
    {
      room_id: roomId,
      category: newCategory,
      player: currentPlayer,
    },
    true,
  );

  if (response.ok) {
    // Esconde o seletor
    const modal = document.getElementById("category-selector");
    if (modal) modal.style.display = "none";

    // Atualiza a interface
    document.getElementById("category").innerText =
      "Categoria: " + data.category;

    // Formata a palavra corretamente
    const formattedWord = data.masked_word;
    document.getElementById("word").innerText = formattedWord;
    document.getElementById("word-length").innerText =
      "Letras: " + data.word_length;

    // Habilita os inputs
    document.getElementById("letter").disabled = false;
    document.getElementById("word-input").disabled = false;

    // Desabilita o botão de próxima rodada até a rodada terminar
    const restartBtn = document.getElementById("restart-btn");
    if (restartBtn) restartBtn.disabled = true;

    // Reseta a forca
    drawHangman(0);

    // Atualiza jogadores
    renderPlayers(data.players, data.player_errors, data.score);

    // Limpa inputs
    document.getElementById("letter").value = "";
    document.getElementById("word-input").value = "";

    showMessage("Category successfully changed!", "green");
  } else {
    showMessage(data.message || "Error when changing category", "red");
  }
}

function getCurrentPlayerErrors(gameData) {
  const token = localStorage.getItem("token");
  if (!token) return 0;

  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    const currentUser = payload.username;
    return gameData.player_errors?.[currentUser] || 0;
  } catch (e) {
    return 0;
  }
}

// Função para criar HTML formatado com espaços visíveis
function formatWordWithSpaces(word) {
  return word
    .split("")
    .map((char) => {
      if (char === " ") {
        return '<span class="space-char">␣</span>';
      }
      return `<span>${char}</span>`;
    })
    .join("");
}

function closeCategorySelector() {
  document.getElementById("category-selector").style.display = "none";
}

window.loadGame = loadGame;
window.guessLetter = guessLetter;
window.guessWord = guessWord;
window.renderPlayers = renderPlayers;
window.restartGame = restartGame;
window.renderCategories = renderCategories;
