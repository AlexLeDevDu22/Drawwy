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
  messages: [],
  allFrames: [],
};

// Drawing configuration
let drawingState = {
  isDrawing: false,
  lastX: 0,
  lastY: 0,
  currentTool: "pencil",
  currentColor: "#000000",
  lineWidth: 5,
  frames: [],
  currentStep: 0,
  undoStack: [],
};

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
function initCanvas() {
  // Set canvas size
  canvas.width = canvas.offsetWidth;
  canvas.height = 400;

  // Clear the canvas
  ctx.fillStyle = "#FFFFFF";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
}

//* Handle WebSocket connection
function handleConnection() {
  let socket = io(gameConfig.serverUrl);

  socket.on("connect", () => {
    console.log("Connecté au serveur WebSocket !");

    // Envoyer un événement 'join' avec le pseudo et l'avatar
    console.log(gameState.pseudo);
    socket.emit("join", {
      pseudo: gameState.pseudo,
      avatar: gameState.avatar,
    });
  });

  // Écouter l'événement 'welcome' pour recevoir l'état initial du jeu
  socket.on("welcome", (data) => {
    console.log("Bienvenue dans la partie :", data);
    gameState.allFrames += data["all_frames"];
    updateCanvasByFrames(data["all_frames"], canvas, false, false);
    gameState.playerId = data["id"];
    gameState.messages = data["messages"];
    gameState.players = data["players"];
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
// Handle update message
function handleUpdate(data) {
  // Update drawer ID
  gameState.drawerId = data.drawer_id;

  // Update drawing if we're not the drawer
  if (data.frames && gameState.playerId !== gameState.drawerId) {
    updateCanvasByFrames(data.frames, canvas);
  }

  // Update current sentence
  if (data.sentence) {
    gameState.currentSentence = data.sentence;
    updateWordDisplay();
  }

  // Add new message if provided
  if (data.new_message) {
    let mess = data.new_message.succeed
      ? data.new_message.pseudo + " à trouvé!"
      : data.new_message.guess;
    addMessageToChat(mess, data.new_message.succeed ? "#63ff6c" : null);
    updatePlayerList();
  }

  // Handle new game
  if (data.new_game) {
    gameState.gameStartTime = new Date(data.new_game);
    gameState.hasFound = false;
    gameState.currentSentence = data.sentence;
    gameState.drawerId = data.drawer_id;

    // Clear the canvas
    initCanvas();
    gameState.allFrames = [];

    // Reset drawing state
    drawingState.frames = [];
    drawingState.currentStep = 0;
    drawingState.undoStack = [];

    // Update UI elements
    updateWordDisplay();

    // Start the timer
    startGameTimer();

    addSystemMessage(
      `Nouvelle partie ! C'est le tour de ${
        getPlayerById(gameState.drawerId).pseudo
      }`
    );

    // If this player is the drawer, enable drawing tools
    toggleDrawingTools();
  }

  if (data.new_founder) {
    for (let i = 0; i < gameState.players.length; i++) {
      if (gameState.players[i].id == data.new_founder)
        gameState.players[i].found = true;
    }
  }

  if (data.new_points) {
    data.new_points.forEach((point) => {
      for (let i = 0; i < gameState.players.length; i++) {
        if (gameState.players[i].id == point.id)
          gameState.players[i].points += point.points;
      }
    });
  }
}

function updateCanvasByFrames(frames, canvas, reset = false, delay = true) {
  if (reset) {
    // Réinitialisation des données globales
    gameState.ALL_FRAMES = [];
    if (canvas) {
      for (let y = 0; y < gameConfig.canvasHeight; y++) {
        canvas[y] = Array(gameConfig.canvasWidth).fill(null);
      }
    } else {
      gameState.CANVAS = Array(gameConfig.canvasHeight)
        .fill()
        .map(() => Array(gameConfig.canvasWidth).fill(null));
    }
  }

  let currentDrawingColor = [0, 0, 0]; // Noir par défaut
  let currentDrawingRadius = 1;

  let newFrames = [...frames]; // Copie des frames
  newFrames = splitStepsByRollback(newFrames, gametate.ROLL_BACK); // Gérer les rollbacks (implémentation non fournie ici)

  // Phase 1 : dessiner
  for (const frame of newFrames[0]) {
    if (frame.type === "draw") {
      const duration = delay ? 1 / frames.length : 0;

      if (frame.color) currentDrawingColor = frame.color;
      if (frame.radius) currentDrawingRadius = frame.radius;

      if (canvas) {
        canvas = drawBrushLine(
          canvas,
          frame.x1,
          frame.y1,
          frame.x2,
          frame.y2,
          currentDrawingColor,
          currentDrawingRadius,
          duration
        );
      } else {
        gameState.CANVAS = drawBrushLine(
          gameState.CANVAS,
          frame.x1,
          frame.y1,
          frame.x2,
          frame.y2,
          currentDrawingColor,
          currentDrawingRadius,
          duration
        );
      }
    }
    S;
    gametate.ALL_FRAMES.push(frame);
  }

  // Phase 2 : ajouter le reste des frames
  for (const frame of newFrames[1]) {
    S;
    gametate.ALL_FRAMES.push(frame);
  }

  if (canvas) return canvas;
}

function drawBrushLine(canvas, x1, y1, x2, y2, color, radius, duration) {
  const height = canvas.length;
  const width = canvas[0].length;

  // Vérifie si une position est dans les limites du canvas
  function inBounds(x, y) {
    return x >= 0 && x < width && y >= 0 && y < height;
  }

  // Dessine un cercle sur le canvas
  function drawCircle(cx, cy) {
    for (let i = -radius; i <= radius; i++) {
      for (let j = -radius; j <= radius; j++) {
        if (i ** 2 + j ** 2 <= radius ** 2) {
          // Points dans un cercle
          const nx = cx + i;
          const ny = cy + j;
          if (inBounds(nx, ny)) {
            canvas[ny][nx] = color;
          }
        }
      }
    }
  }

  // Dessine une ligne épaisse et lisse
  function drawThickLine(x1, y1, x2, y2) {
    const dx = x2 - x1;
    const dy = y2 - y1;
    const dist = Math.max(Math.abs(dx), Math.abs(dy));

    const stepDuration = duration / dist;
    for (let step = 0; step <= dist; step++) {
      const t = step / dist;
      const x = Math.round(x1 + t * dx);
      const y = Math.round(y1 + t * dy);
      drawCircle(x, y); // Dessine un cercle autour de chaque point

      // Ajoute un délai si nécessaire
      if (stepDuration > 0) {
        const delay = Math.max(0, stepDuration - 0.004); // Ajuste la durée du délai
        sleep(delay);
      }
    }
  }

  // Dessine la ligne et les extrémités arrondies
  drawThickLine(x1, y1, x2, y2);
  drawCircle(x1, y1);
  drawCircle(x2, y2);

  return canvas;
}

// Fonction sleep (asynchrone pour simuler les délais)
function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms * 1000));
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

function addMessageToChat(message, color) {
  chatMessages.innerHTML += `<div class="message system-message" ${
    'style="background-color: ' + (color || "#var(--light-color)") + '"'
  }>${message}</div>`;
}

// Update word display based on current game state
function updateWordDisplay() {
  if (!gameState.currentSentence) {
    hintText.textContent = "En attente de joueurs...";
    return;
  }

  if (gameState.playerId === gameState.drawerId) {
    // If player is the drawer, show the full word
    hintText.textContent = `Mot à dessiner : ${gameState.currentSentence}`;
  } else if (gameState.hasFound) {
    // If player has found the word
    hintText.textContent = `Vous avez trouvé : ${gameState.currentSentence}`;
  } else {
    // Otherwise show hints (first letter and length)
    const firstLetter = gameState.currentSentence.charAt(0);
    const hint = firstLetter + "_".repeat(gameState.currentSentence.length - 1);
    hintText.textContent = `Mot à deviner : ${hint}`;
  }
}

// Start game timer
function startGameTimer() {
  gameState.remainingTime = gameConfig.gameDuration;
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

//! Events

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
