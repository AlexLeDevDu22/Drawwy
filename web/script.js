//! Game Configuration
const gameConfig = {
  gameDuration: 150, // seconds
  canvasWidth: 200,
  canvasHeight: 200,
  serverUrl: "https://vital-mastiff-publicly.ngrok-free.app",
};

// Game state
let gameState = {
  playerId: null,
  players: [],
  drawerId: null,
  avatar: { emoji: null, color: null },
  isDrawing: false,
  currentSentence: "",
  gameStartTime: null,
  remainingTime: gameConfig.gameDuration,
  hasFound: false,
  allFrames: [],
  undoStack: [],
  drawingState: {
    currentColor: "#000000",
    lineWidth: 5,
  },
};

// Drawing configuration

//! DOM elements
const loginOverlay = document.getElementById("login-overlay");
const loginForm = document.getElementById("login-form");
const pseudoInput = document.getElementById("pseudo-input");
const loginButton = document.getElementById("login-btn");
const avatarSelection = document.getElementById("avatar-selection");
const avatarOptions = document.querySelectorAll(".avatar-option");
const playerList = document.getElementById("player-list");
const wordDisplay = document.getElementById("word-display");
const hintText = document.getElementById("hint-text");
const timerText = document.getElementById("timer-text");
const timerProgress = document.getElementById("timer-progress");
const canvas = document.getElementById("drawing-canvas");
const ctx = canvas.getContext("2d");
const toolButtons = document.querySelectorAll(".tool-btn");
const colorOptions = document.querySelectorAll(".color-option");
const sizeSlider = document.getElementById("size-slider");
const chatMessages = document.getElementById("chat-messages");
const chatInput = document.getElementById("chat-input");
const sendBtn = document.getElementById("send-btn");
const drawingTools = document.getElementById("drawing-tools");
const gameModal = document.getElementById("game-modal");
const resultInfo = document.getElementById("result-info");
const wordReveal = document.getElementById("word-reveal");
const continueBtn = document.getElementById("continue-btn");

//! Functions
// Initialize the canvas
function clearCanvas() {
  // Set canvas size
  canvas.width = canvas.offsetWidth;
  canvas.height = canvas.offsetWidth;

  // Clear the canvas
  ctx.fillStyle = "#FFFFFF";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
}

//* Handle WebSocket connection
var socket = null;
function handleConnection() {
  socket = io(gameConfig.serverUrl);

  socket.on("connect", () => {
    console.log("Connecté au serveur WebSocket !");

    // Envoyer un événement 'join' avec le pseudo et l'avatar
    console.log(gameState.pseudo);
    socket.emit("join", {
      pseudo: gameState.pseudo,
      avatar: gameState.avatar,
    });
  });

  socket.on("disconnect", () => {
    console.log("Déconnexion du serveur WebSocket.");

    clearCanvas();
    chatMessages.innerHTML = "";
    playerList.innerHTML = "";
  });

  // Écouter l'événement 'welcome' pour recevoir l'état initial du jeu
  socket.on("welcome", (data) => {
    console.log("Bienvenue dans la partie :", data);
    gameState.allFrames += data.all_frames;
    console.log("start frames", data.all_frames);
    if (data.all_frames.length > 0) draw(data.all_frames, false);
    gameState.playerId = data["id"];
    data["messages"].forEach((message) => {
      addMessageToChat(
        message.guess,
        message.succeed ? "#63ff6c" : null,
        message.pseudo,
        message.pid,
        message.succeed
      );
    });
    gameState.players = data.players;
    updatePlayerList();

    gameState.gameStartTime = new Date(data.new_game);
    startGameTimer();
  });

  socket.on("new_player", (data) => {
    console.log("Nouveaux joueurs :", data);
    gameState.players.push(data);
    updatePlayerList();
    addMessageToChat(gameState.pseudo + " viens de nous rejoindre!", "#63ff6c");
  });

  socket.on("draw", (frames) => {
    console.log("Mise à jour du dessin");
    gameState.allFrames += frames;
    gameState.drawingState.undoStack = [];
    draw(frames, true);
  });

  socket.on("roll_back", (roll_back) => {
    console.log("Roll back");
    //resplit frames and undo stacks
    gameState.allFrames += gameState.drawingState.undoStack;
    gameState.drawingState.undoStack = gameState.allFrames.slice(-roll_back);

    clearCanvas();
    draw(gameState.allFrames, false);
  });

  socket.on("new_message", (data) => {
    console.log("Nouveau message :", data);
    addMessageToChat(
      data.message.guess,
      data.succeed ? "#63ff6c" : null,
      data.message.pseudo,
      data.message.pid,
      data.message.succeed
    );

    if (data.new_founder) {
      for (let i = 0; i < gameState.players.length; i++) {
        if (gameState.players[i].id == data.new_founder)
          gameState.players[i].found = true;
      }
      data.new_points.forEach((point) => {
        for (let i = 0; i < gameState.players.length; i++) {
          if (gameState.players[i].id == point.id)
            gameState.players[i].points += point.points;
        }
      });
    }
  });

  socket.on("new_game", (data) => {
    console.log("Nouvelle partie :", data);

    clearCanvas();
    gameState.allFrames = [];
    gameState.currentSentence = data.new_sentence;
    gameState.drawerId = data.drawer_id;
    gameState.hasFound = false;
    addMessageToChat(
      "Nouvelle partie ! " +
        gameState.players.find((p) => p.id == gameState.drawerId)["pseudo"] +
        " deviens le dessinateur !"
    );
    gameState.gameStartTime = new Date(data.start_time);

    updateWordDisplay();

    // If this player is the drawer, enable drawing tools
    toggleDrawingTools();
  });

  socket.on("player_disconnected", (data) => {
    console.log("Joueur déconnecté :", data);
    gameState.players = gameState.players.filter(
      (player) => player.id !== data.id
    );
    updatePlayerList();
    addMessageToChat(gameState.pseudo + " à quitté la partie.", "#fc6455");
  });

  // Écouter les mises à jour du jeu
  socket.on("update", (data) => {
    console.log("Mise à jour du jeu :", data);
  });
}

function draw(frames, delay) {
  if (!frames || frames.length === 0) return;

  const gameWidth = 200; // Taille logique du jeu
  const gameHeight = 200;

  const realWidth = canvas.offsetWidth; // Taille réelle sur la page
  const realHeight = canvas.offsetHeight;

  const scaleX = realWidth / gameWidth; // Facteur d'échelle horizontal
  const scaleY = realHeight / gameHeight; // Facteur d'échelle vertical
  const scale = Math.min(scaleX, scaleY); // Assurer une échelle uniforme

  let totalDuration = 1000; // On suppose que ça a pris 1s pour faire tous les traits
  let frameDuration = totalDuration / frames.length; // Temps moyen entre chaque trait

  let color = null;

  function drawLine(frame) {
    if (frame.color) color = frame.color;
    ctx.strokeStyle = color;
    ctx.lineWidth = frame.radius * 2 * scale; // Adapter la taille du crayon

    ctx.beginPath();
    ctx.moveTo(frame.x1 * scaleX, frame.y1 * scaleY);
    ctx.lineTo(frame.x2 * scaleX, frame.y2 * scaleY);
    ctx.stroke();
  }

  if (delay) {
    frames.forEach((frame, index) => {
      setTimeout(() => drawLine(frame), index * frameDuration);
    });
  } else {
    frames.forEach(drawLine);
  }
}

function toggleDrawingTools() {
  drawingTools.style.opacity = gameState.playerId == gameState.drawerId ? 1 : 0;
}

// Update player list UI
function updatePlayerList() {
  playerList.innerHTML = "";

  gameState.players.forEach((player) => {
    const playerItem = document.createElement("li");
    playerItem.className = "player-item";

    // Add classes based on player status
    if (player.id === gameState.drawerId) {
      playerItem.classList.add("current-drawer");
    }

    if (player.found) {
      playerItem.classList.add("found");
    }

    playerItem.innerHTML =
      (player.avatar.type == "emoji"
        ? `
            <div class="avatar" style="background-color: rgb(${player.avatar.color[0]}, ${player.avatar.color[1]}, ${player.avatar.color[2]})">${player.avatar.emoji} </div>`
        : `<img class="avatar" src="players-avatars/${player.id}.bmp">`) +
      `<div class="player-info">
                <div class="player-name-found">
                    <div class="player-name">${player.pseudo}${
        player.id === gameState.playerId ? " (Vous)" : ""
      }</div>
                    ${
                      player.found
                        ? '<svg xmlns="http://www.w3.org/2000/svg" class="player-found-icon" viewBox="0 0 512 512" fill="#63ff6c"><path d="M256 512A256 256 0 1 0 256 0a256 256 0 1 0 0 512zM369 209L241 337c-9.4 9.4-24.6 9.4-33.9 0l-64-64c-9.4-9.4-9.4-24.6 0-33.9s24.6-9.4 33.9 0l47 47L335 175c9.4-9.4 24.6-9.4 33.9 0s9.4 24.6 0 33.9z"/></svg>'
                        : '<svg xmlns="http://www.w3.org/2000/svg" class="player-found-icon" viewBox="0 0 512 512" fill="#333"><path d="M256 48a208 208 0 1 1 0 416 208 208 0 1 1 0-416zm0 464A256 256 0 1 0 256 0a256 256 0 1 0 0 512zM175 175c-9.4 9.4-9.4 24.6 0 33.9l47 47-47 47c-9.4 9.4-9.4 24.6 0 33.9s24.6 9.4 33.9 0l47-47 47 47c9.4 9.4 24.6 9.4 33.9 0s9.4-24.6 0-33.9l-47-47 47-47c9.4-9.4 9.4-24.6 0-33.9s-24.6-9.4-33.9 0l-47 47-47-47c-9.4-9.4-24.6-9.4-33.9 0z"/></svg>'
                    }
                </div>
                <div class="player-score">${player.points} points</div>
            </div>
            <div>
                ${
                  player.id === gameState.drawerId
                    ? '<span class="player-status status-drawing">Dessine</span>'
                    : ""
                }
                ${
                  player.found
                    ? '<span class="player-status status-found">Trouvé !</span>'
                    : ""
                }
            </div>
        `;

    playerList.appendChild(playerItem);
  });
}

function addMessageToChat(message, color, messPseudo, pid, succeed) {
  if (messPseudo) {
    let pseudo = document.createElement("p");
    pseudo.textContent = messPseudo;
    pseudo.className = "chat-pseudo";
    chatMessages.appendChild(pseudo);
  }

  let divMessage = document.createElement("div");
  divMessage.textContent = message;
  divMessage.classList.add("message");
  divMessage.classList.add(messPseudo ? "player-message" : "system-message");
  if (pid === gameState.playerId) divMessage.classList.add(`my-message`);
  if (pid === gameState.drawerId) divMessage.classList.add(`message-author`);
  if (succeed) divMessage.classList.add(`correct-guess`);

  divMessage.style.backgroundColor = color || "#var(--light-color)";

  chatMessages.appendChild(divMessage);

  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Update word display based on current game state
function updateWordDisplay() {
  if (!gameState.currentSentence) {
    hintText.textContent = "En attente de joueurs...";
    return;
  }

  if (gameState.playerId === gameState.drawerId) {
    // If player is the drawer, show the full word
    hintText.textContent = `Dessinez : ${gameState.currentSentence}`;
  } else if (gameState.hasFound) {
    // If player has found the word
    hintText.textContent = `Vous avez trouvé : ${gameState.currentSentence}`;
  } else {
    hintText.textContent = `A vous de deviner`;
  }
}

// Start game timer
function startGameTimer() {
  gameState.remainingTime = gameConfig.gameDuration;
  timerProgress.classList.remove("not-star");
  updateTimerDisplay();

  const timerInterval = setInterval(() => {
    const now = new Date();
    const elapsedSeconds = Math.floor((now - gameState.gameStartTime) / 1000);
    gameState.remainingTime = Math.max(
      0,
      gameConfig.gameDuration - elapsedSeconds
    );

    updateTimerDisplay();

    if (gameState.remainingTime <= 0) {
      clearInterval(timerInterval);
      handleGameEnd();
    }
  }, 1000);
}

// Update timer display
function updateTimerDisplay() {
  const minutes = Math.floor(gameState.remainingTime / 60);
  const seconds = gameState.remainingTime % 60;
  timerText.textContent = `${minutes}:${seconds.toString().padStart(2, "0")}`;

  // Update progress bar
  const progressPercent =
    (gameState.remainingTime / gameConfig.gameDuration) * 100;
  timerProgress.style.width = `${progressPercent}%`;

  // Change color as time runs out
  if (progressPercent < 30) {
    timerProgress.style.color = "red";
  } else {
    timerProgress.style.color = "#333";
  }
}

function handleGameEnd() {}

//! Events Listeners

//* login
let selectedAvatar = null;
avatarOptions.forEach((option) => {
  option.addEventListener("click", () => {
    if (selectedAvatar) selectedAvatar.classList.remove("selected");

    gameState.avatar = {
      type: "emoji",
      emoji: option.getAttribute("data-avatar"),
      color: option.style.backgroundColor.match(/\d+/g).map(Number), // convert to rgb list
    };
    option.classList.add("selected");

    selectedAvatar = option;
  });
});

loginForm.addEventListener("submit", (e) => {
  e.preventDefault();
  if (selectedAvatar) {
    loginOverlay.style.opacity = 0;
    loginOverlay.style.pointerEvents = "none";

    gameState.pseudo = pseudoInput.value;

    handleConnection();
  }
});

// send message
function sendMessage(message) {
  if (message) {
    socket.emit("guess", {
      pid: gameState.playerId,
      guess: message,
      game_remaining_time: gameState.remainingTime,
    });
  }
}

sendBtn.addEventListener("click", () => {
  if (chatInput.value == "") return;
  sendMessage(chatInput.value);
  chatInput.value = "";
});

chatInput.addEventListener("keypress", (key) => {
  if (chatInput.value == "" || key.key != "Enter") return;
  sendMessage(chatInput.value);
  chatInput.value = "";
});
