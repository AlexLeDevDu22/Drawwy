//! Game Configuration
const gameConfig = {
  gameDuration: 150, // seconds
  canvasWidth: 200,
  canvasHeight: 200,
  serverUrl: "https://vital-mastiff-publicly.ngrok-free.app",
};

// Game state
let myId = null;
let players = [];
let drawerId = null;
let avatar = { emoji: null, color: null };
let currentSentence = "";
let gameStartTime = null;
let remainingTime = gameConfig.gameDuration;
let hasFound = false;
let allFrames = [];
let undoStack = [];
let drawingState = {
  color: "#000000",
  radius: 5,
  isDrawing: false,
  lastPos: null,
  currentStroke: [],
  drawFrames: [],
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
const chatMessages = document.getElementById("chat-messages-container");
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
  canvas.width = gameConfig.canvasWidth;
  canvas.height = gameConfig.canvasHeight;

  // Clear the canvas
  ctx.fillStyle = "#FFFFFF";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
}
clearCanvas();

//* Handle WebSocket connection
var socket = null;
function handleConnection() {
  socket = io(gameConfig.serverUrl);

  socket.on("connect", () => {
    console.log("Connecté au serveur WebSocket !");

    // Envoyer un événement 'join' avec le pseudo et l'avatar
    console.log(pseudo);
    setTimeout(() => {
      // etre connecté après python
      socket.emit("join", {
        pseudo: pseudo,
        avatar: avatar,
      });
    }, 100);
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
    allFrames += data.all_frames;
    console.log("start frames", data.all_frames);
    if (data.all_frames.length > 0) draw(data.all_frames, false);
    myId = data["id"];
    data["messages"].forEach((message) => {
      addMessageToChat(
        message.message,
        message.succeed ? "#63ff6c" : null,
        message.pseudo,
        message.pid,
        message.succeed
      );
    });
    players = data.players;
    currentSentence = data.sentence;
    drawerId = data.drawer_id;
    gameStartTime = new Date(data.new_game);
    updatePlayerList();
    updateWordDisplay();
    toggleDrawingTools();
    startGameTimer();
  });

  socket.on("new_player", (data) => {
    console.log("Nouveaux joueurs :", data);
    players.push(data);
    updatePlayerList();
    addMessageToChat(pseudo + " viens de nous rejoindre!", "#63ff6c");
  });

  socket.on("draw", (frames) => {
    console.log("Mise à jour du dessin");
    allFrames += frames;
    drawingState.undoStack = [];
    draw(frames, true);
  });

  socket.on("roll_back", (roll_back) => {
    console.log("Roll back");
    //resplit frames and undo stacks
    allFrames += drawingState.undoStack;
    drawingState.undoStack = allFrames.slice(-roll_back);

    clearCanvas();
    draw(allFrames, false);
  });

  socket.on("new_message", (guess) => {
    console.log("Nouveau guess :", guess);
    addMessageToChat(
      guess.message,
      guess.succeed ? "#63ff6c" : null,
      guess.pseudo,
      guess.pid,
      guess.succeed
    );

    if (guess.succeed) {
      for (let i = 0; i < players.length; i++) {
        if (players[i].id == guess.pid) players[i].found = true;

        guess.new_points.forEach((point) => {
          if (players[i].id == point.pid) players[i].points += point.points;
        });
      }

      updatePlayerList();
    }
  });

  socket.on("new_game", (data) => {
    console.log("Nouvelle partie :", data);

    clearCanvas();
    allFrames = [];
    currentSentence = data.new_sentence;
    drawerId = data.drawer_id;
    hasFound = false;
    players.forEach((p) => (p.found = false));
    console.log(players, drawerId);
    addMessageToChat(
      "Nouvelle partie, " +
        players.find((p) => p.id == drawerId)["pseudo"] +
        " deviens le dessinateur !",
      "#63ff6c"
    );
    gameStartTime = new Date(data.start_time);

    updateWordDisplay();
    updatePlayerList();
    toggleDrawingTools();
  });

  socket.on("player_disconnected", (data) => {
    console.log("Joueur déconnecté :", data);
    players = players.filter((player) => player.id !== data.pid);
    updatePlayerList();
    addMessageToChat(data.pseudo + " à quitté la partie.", "#fc6455");
  });

  // Écouter les mises à jour du jeu
  socket.on("update", (data) => {
    console.log("Mise à jour du jeu :", data);
  });
}

function draw(frames, delay) {
  if (!frames || frames.length === 0) return;

  let totalDuration = 1000; // On suppose que ça a pris 1s pour faire tous les traits
  let frameDuration = totalDuration / frames.length; // Temps moyen entre chaque trait

  let color = null;
  let radius = null;

  console.log(frames);
  if (delay) {
    frames.forEach((frame, index) => {
      setTimeout(() => {
        if (frame.color)
          color = `rgb(${frame.color[0]}, ${frame.color[1]}, ${frame.color[2]})`;
        if (frame.radius) radius = frame.radius / 4;

        drawLine(frame.x1, frame.y1, frame.x2, frame.y2, color, radius);
      }, index * frameDuration);
    });
  } else {
    frames.forEach(drawLine);
  }
}

function drawLine(x1, y1, x2, y2, color, radius) {
  ctx.strokeStyle = color;
  ctx.fillStyle = color;
  ctx.lineWidth = 1; // Adapter l'épaisseur du trait

  // Tracer une ligne entre x1 et x2
  ctx.beginPath();
  ctx.moveTo(x1, y1);
  ctx.lineTo(x2, y2);
  ctx.stroke();

  // Ajouter des cercles aux extrémités pour lisser et bien remplir
  ctx.beginPath();
  ctx.arc(x1, y1, Math.max(1, radius / 4), 0, 2 * Math.PI);
  ctx.fill(); // Remplir le cercle
  ctx.beginPath();
  ctx.arc(x2, y2, Math.max(1, radius / 4), 0, 2 * Math.PI);
  ctx.fill(); // Remplir le cercle
}

function toggleDrawingTools() {
  drawingTools.style.opacity = myId == drawerId ? 1 : 0;
}

// Update player list UI
function updatePlayerList() {
  playerList.innerHTML = "";

  players.forEach((player) => {
    const playerItem = document.createElement("li");
    playerItem.className = "player-item";

    // Add classes based on player status
    if (player.id == drawerId) {
      playerItem.classList.add("current-drawer");
    }
    console.log(player.id, drawerId);

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
                    <div class="player-name${
                      player.id === myId ? " me" : ""
                    }">${player.pseudo}</div>
                    ${
                      player.id != drawerId
                        ? player.found
                          ? '<svg xmlns="http://www.w3.org/2000/svg" class="player-found-icon" viewBox="0 0 512 512" fill="#63ff6c"><path d="M256 512A256 256 0 1 0 256 0a256 256 0 1 0 0 512zM369 209L241 337c-9.4 9.4-24.6 9.4-33.9 0l-64-64c-9.4-9.4-9.4-24.6 0-33.9s24.6-9.4 33.9 0l47 47L335 175c9.4-9.4 24.6-9.4 33.9 0s9.4 24.6 0 33.9z"/></svg>'
                          : '<svg xmlns="http://www.w3.org/2000/svg" class="player-found-icon" viewBox="0 0 512 512" fill="#333"><path d="M256 48a208 208 0 1 1 0 416 208 208 0 1 1 0-416zm0 464A256 256 0 1 0 256 0a256 256 0 1 0 0 512zM175 175c-9.4 9.4-9.4 24.6 0 33.9l47 47-47 47c-9.4 9.4-9.4 24.6 0 33.9s24.6 9.4 33.9 0l47-47 47 47c9.4 9.4 24.6 9.4 33.9 0s9.4-24.6 0-33.9l-47-47 47-47c9.4-9.4 9.4-24.6 0-33.9s-24.6-9.4-33.9 0l-47 47-47-47c-9.4-9.4-24.6-9.4-33.9 0z"/></svg>'
                        : ""
                    }
                </div>
                <div class="player-score">${player.points} points</div>
            </div>
            <div>
                ${
                  player.id === drawerId
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
  if (messPseudo && !succeed) {
    let pseudo = document.createElement("p");
    pseudo.textContent = messPseudo;
    pseudo.className = "chat-pseudo";
    if (pid == myId) pseudo.classList.add(`my-pseudo`);
    chatMessages.appendChild(pseudo);
  }

  message = succeed ? messPseudo + " à trouvé!" : message;
  let divMessage = document.createElement("div");
  divMessage.textContent = message;
  divMessage.classList.add("message");
  divMessage.classList.add(messPseudo ? "player-message" : "system-message");
  if (pid == myId) divMessage.classList.add(`my-message`);
  if (pid == drawerId) divMessage.classList.add(`message-author`);
  if (succeed) divMessage.classList.add(`correct-guess`);

  divMessage.style.backgroundColor = color || "#var(--light-color)";

  chatMessages.appendChild(divMessage);

  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Update word display based on current game state
function updateWordDisplay() {
  if (players.length == 1) {
    hintText.textContent = "En attente de joueurs...";
    return;
  }

  if (myId === drawerId) {
    // If player is the drawer, show the full word
    hintText.textContent = `Dessinez : ${currentSentence}`;
  } else if (hasFound) {
    // If player has found the word
    hintText.textContent = `Vous avez trouvé : ${currentSentence}`;
  } else {
    hintText.textContent = `A vous de deviner`;
  }
}

// Start game timer
function startGameTimer() {
  remainingTime = gameConfig.gameDuration;
  timerProgress.classList.remove("not-started");
  updateTimerDisplay();

  const timerInterval = setInterval(() => {
    const now = new Date();
    const elapsedSeconds = Math.floor((now - gameStartTime) / 1000);
    remainingTime = Math.max(0, gameConfig.gameDuration - elapsedSeconds);

    updateTimerDisplay();

    if (remainingTime <= 0) {
      clearInterval(timerInterval);
      handleGameEnd();
    }
  }, 1000);
}

// Update timer display
function updateTimerDisplay() {
  const minutes = Math.floor(remainingTime / 60);
  const seconds = remainingTime % 60;
  timerText.textContent = `${minutes}:${seconds.toString().padStart(2, "0")}`;

  // Update progress bar
  const progressPercent = (remainingTime / gameConfig.gameDuration) * 100;
  timerProgress.style.width = `${progressPercent}%`;

  // Change color as time runs out
  if (progressPercent < 30) {
    timerProgress.style.color = "red";
  } else {
    timerProgress.style.color = "#333";
  }
}

function handleGameEnd() {
  clearCanvas();
  if (myId == drawerId) socket.emit("game_finished", null);
}

//! Events Listeners

//* login
let selectedAvatar = null;
avatarOptions.forEach((option) => {
  option.addEventListener("click", () => {
    if (selectedAvatar) selectedAvatar.classList.remove("selected");

    avatar = {
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

    pseudo = pseudoInput.value;
    handleConnection();
  }
});

// send message
function sendMessage(message) {
  if (message) {
    socket.emit("guess", {
      pid: myId,
      pseudo: pseudo,
      message: message,
      remaining_time: remainingTime,
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

//! draw

canvas.addEventListener("mousedown", (e) => {
  drawingState.isDrawing = true;
  drawingState.lastPos = getMousePos(e);
  drawingState.currentStroke.push({ type: "new_step" });
});

canvas.addEventListener("mousemove", (e) => {
  if (!drawingState.isDrawing || myId != drawerId) return;

  const pos = getMousePos(e);
  if (drawingState.lastPos) {
    console.log(pos);
    drawLine(
      drawingState.lastPos.x,
      drawingState.lastPos.y,
      pos.x,
      pos.y,
      drawingState.color,
      drawingState.radius
    );
    const frame = {
      type: "line",
      x1: drawingState.lastPos.x,
      y1: drawingState.lastPos.y,
      x2: pos.x,
      y2: pos.y,
      color: drawingState.color,
      radius: drawingState.radius,
    };
    drawingState.currentStroke.push(frame);
    allFrames.push(frame);

    drawingState.lastPos = pos;
  }
});

canvas.addEventListener("mouseup", () => {
  drawingState.isDrawing = false;
  drawingState.lastPos = null;
  if (drawingState.currentStroke.length > 1)
    drawingState.drawFrames.push(...drawingState.currentStroke);
  drawingState.currentStroke = [];
});

function getMousePos(e) {
  const rect = canvas.getBoundingClientRect();
  return {
    x: parseInt((canvas.width / canvas.clientWidth) * (e.clientX - rect.left)),
    y: parseInt((canvas.height / canvas.clientHeight) * (e.clientY - rect.top)),
  };
}

function parseFrames(frames) {
  function hexToRGB(hex) {
    let bigint = parseInt(hex.replace(/^#/, ""), 16);
    return [(bigint >> 16) & 255, (bigint >> 8) & 255, bigint & 255];
  }

  let color = null,
    radius = null;
  frames.forEach((frame, i) => {
    if (frame.type == "line") {
      frame.color = hexToRGB(frame.color);
      if (frame.color == color) delete frames[i].color;
      if (frame.radius == radius) delete frames[i].radius;
      color = frame.color;
      radius = frame.radius;
    }
  });
  return frames;
}

setInterval(() => {
  if (drawingState.drawFrames.length > 0) {
    const newFrames = parseFrames(drawingState.drawFrames);
    console.log("Envoi du dessin", newFrames);
    socket.emit("draw", newFrames);
    drawingState.drawFrames = [];
  }
}, 1000);

colorOptions.forEach((option) => {
  option.addEventListener("click", () => {
    drawingState.color = option.getAttribute("data-color");
    colorOptions
      .find((option) => option.classList.contains(".active"))
      .classList.remove("active");
    option.classList.add("active");
  });
});

sizeSlider.addEventListener("input", (event) => {
  drawingState.radius = parseInt(event.target.value);
});
