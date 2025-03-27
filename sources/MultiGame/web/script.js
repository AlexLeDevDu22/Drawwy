//! Game Configuration
const gameConfig = {
  gameDuration: 180, // seconds
  canvasWidth: 200,
  canvasHeight: 200,
  serverUrl: "https://vital-mastiff-publicly.ngrok-free.app",
};

// Game state
let myId = null;
let players = [];
let drawerId = null;
let avatar = { emoji: null, color: null, has_border: false };
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

  canvas.style.width = canvas.getClientRects().width + "px";

  // Clear the canvas
  ctx.fillStyle = "#FFFFFF";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
}
clearCanvas();

//* Handle WebSocket connection
var socket = null;
/**
 * Handle the WebSocket connection
 * @function handleConnection
 * @param {string} pseudo - The player's pseudo
 * @param {object} avatar - The player's avatar object
 * @param {object} players - The list of players
 */
function handleConnection() {
  // Create a WebSocket connection
  socket = new WebSocket(`wss://${window.location.host}/ws`);

  socket.onopen = function () {
    console.log("Connecté au serveur WebSocket !");

    // Send join message with header field
    setTimeout(() => {
      socket.send(
        JSON.stringify({
          header: "join",
          pseudo: pseudo,
          avatar: avatar,
        })
      );
    }, 100);
  };

  socket.onclose = function () {
    console.log("Déconnexion du serveur WebSocket.");

    clearCanvas();
    chatMessages.innerHTML = "";
    playerList.innerHTML = "";
  };

  /**
   * Handle a message from the server
   * @param {MessageEvent} event - The WebSocket message event
   * @listens WebSocket#message
   */
  socket.onmessage = function (event) {
    const data = JSON.parse(event.data);

    // Handle different message types based on the header
    switch (data.header) {
      case "welcome":
        console.log("Bienvenue dans la partie :", data);
        allFrames.concat(data.all_frames);
        console.log("start frames", data.all_frames);
        if (data.all_frames.length > 0) draw(data.all_frames, false);
        myId = data["pid"];
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
        drawerId = data.drawer_pid;
        gameStartTime = new Date(data.new_game);
        updatePlayerList();
        updateWordDisplay();
        toggleDrawingTools();
        break;

      case "new_player":
        console.log("Nouveaux joueurs :", data);
        players.push(data);
        updatePlayerList();
        addMessageToChat(pseudo + " viens de nous rejoindre!", "#63ff6c");
        break;

      case "draw":
        console.log("Mise à jour du dessin");
        allFrames.concat(data.frames);
        drawingState.undoStack = [];
        draw(data.frames, true);
        break;

      case "roll_back":
        console.log("Roll back");
        allFrames.concat(drawingState.undoStack);
        drawingState.undoStack = allFrames.slice(-data.roll_back);

        clearCanvas();
        draw(allFrames, false);
        break;

      case "new_message":
        console.log("Nouveau mess :", data);
        if (data.type == "guess")
          addMessageToChat(
            data.message,
            data.succeed ? "#63ff6c" : null,
            data.pseudo,
            data.pid,
            data.succeed
          );
        else if (data.type == "emote")
          addEmoteToChat(data.emote_path, data.pseudo, data.pid);

        if (data.succeed) {
          for (let i = 0; i < players.length; i++) {
            if (players[i].pid == data.pid) players[i].found = true;

            data.new_points.forEach((point) => {
              if (players[i].pid == point.pid)
                players[i].points += point.points;
            });
          }

          updatePlayerList();
        }
        break;

      case "new_game":
        console.log("Nouvelle partie :", data);

        clearCanvas();
        allFrames = [];
        currentSentence = data.new_sentence;
        drawerId = data.drawer_pid;
        hasFound = false;
        players.forEach((p) => (p.found = false));
        console.log(players, drawerId);
        addMessageToChat(
          "Nouvelle partie, " +
            players.find((p) => p.pid == drawerId)["pseudo"] +
            " deviens le dessinateur !",
          "#63ff6c"
        );
        gameStartTime = new Date(data.start_time);

        updateWordDisplay();
        updatePlayerList();
        toggleDrawingTools();
        startGameTimer();
        break;

      case "player_disconnected":
        if (data.pid != myId) {
          console.log("Joueur déconnecté :", data);
          players = players.filter((player) => player.pid !== data.pid);
          updatePlayerList();
          addMessageToChat(data.pseudo + " à quitté la partie.", "#fc6455");
        }
        break;

      default:
        console.log("Mise à jour du jeu :", data);
    }
  };
}

/**
 * Dessine les frames sur le canvas.
 * Si delay est vrai, dessine les frames en prenant en compte le temps entre chaque trait.
 * Si delay est faux, dessine les frames immédiatement.
 * @param {Frame[]} frames - Les frames à dessiner.
 * @param {boolean} delay - Si il faut dessiner les frames avec un délai ou non.
 */
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

      setTimeout(() => {
        isDrawing = false;
      }, totalDuration);
    });
  } else {
    frames.forEach(drawLine);
  }
}

/**
 * Dessine une ligne sur le canvas.
 * @param {number} x1 - Coordonnée x du point de départ.
 * @param {number} y1 - Coordonnée y du point de départ.
 * @param {number} x2 - Coordonnée x du point d'arrivée.
 * @param {number} y2 - Coordonnée y du point d'arrivée.
 * @param {string} color - La couleur de la ligne.
 * @param {number} radius - Le rayon des cercles aux extrémités.
 */
function drawLine(x1, y1, x2, y2, color, radius) {
  ctx.strokeStyle = color;
  ctx.fillStyle = color;
  ctx.lineWidth = radius * 2; // Adapter l'épaisseur du trait

  // Tracer une ligne entre x1 et x2
  ctx.beginPath();
  ctx.moveTo(x1, y1);
  ctx.lineTo(x2, y2);
  ctx.stroke();

  // Ajouter des cercles aux extrémités pour lisser et bien remplir
  ctx.beginPath();
  ctx.arc(x1, y1, Math.max(1, radius), 0, 2 * Math.PI);
  ctx.fill(); // Remplir le cercle
  ctx.beginPath();
  ctx.arc(x2, y2, Math.max(1, radius), 0, 2 * Math.PI);
  ctx.fill(); // Remplir le cercle
}

/**
 * Toggle the opacity of the drawing tools based on whether the player is the current drawer or not.
 */
function toggleDrawingTools() {
  drawingTools.style.opacity = myId == drawerId ? 1 : 0;
}

/**
 * Updates the player list.
 * It clears the player list and regenerates all the player items.
 * It adds classes based on player status.
 * If the player is the current drawer, it adds a class to the player item.
 * If the player has found the word, it adds a class to the player item.
 */
function updatePlayerList() {
  playerList.innerHTML = "";

  players.forEach((player) => {
    const playerItem = document.createElement("li");
    playerItem.className = "player-item";

    // Add classes based on player status
    if (player.pid == drawerId) {
      playerItem.classList.add("current-drawer");
    }
    console.log(player.pid, drawerId);

    if (player.found) {
      playerItem.classList.add("found");
    }

    playerItem.innerHTML =
      (player.avatar.type == "emoji"
        ? `
            <div class="avatar" style="background-color: rgb(${player.avatar.color[0]}, ${player.avatar.color[1]}, ${player.avatar.color[2]})">${player.avatar.emoji} </div>`
        : `<img class="avatar" src="temp-assets/avatars/${player.pid}.bmp">`) +
      `<div class="player-info">
                <div class="player-name-found">
                    <div class="player-name${
                      player.pid === myId ? " me" : ""
                    }">${player.pseudo}</div>
                    ${
                      player.pid != drawerId
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
                  player.pid === drawerId
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

/**
 * Adds a message to the chat with the given text, color, and author.
 * If an author is given and the message is not a success message, it adds a pseudo above the message.
 * If the message is a success message, it changes the message text to indicate that the author has found the word.
 * It adds classes to the message to indicate its type and author.
 * Finally, it scrolls the chat to the bottom.
 * @param {string} message - The text of the message.
 * @param {string} [color] - The background color of the message.
 * @param {string} [messPseudo] - The pseudo of the author of the message if it is a player message.
 * @param {number} [pid] - The ID of the author of the message if it is a player message.
 * @param {boolean} [succeed] - If the message is a success message.
 */
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

/**
 * Adds an emote to the chat with the given path and author.
 * If an author is given, it adds a pseudo above the emote.
 * It adds classes to the emote to indicate its type and author.
 * Finally, it scrolls the chat to the bottom.
 * @param {string} emotePath - The path of the emote asset.
 * @param {string} [messPseudo] - The pseudo of the author of the emote if it is a player emote.
 * @param {number} [pid] - The ID of the author of the emote if it is a player emote.
 */
function addEmoteToChat(emotePath, messPseudo, pid) {
  let pseudo = document.createElement("p");
  pseudo.textContent = messPseudo;
  pseudo.className = "chat-pseudo";
  if (pid == myId) pseudo.classList.add(`my-pseudo`);
  pseudo.style.marginBottom = "0";
  chatMessages.appendChild(pseudo);

  const emoteElement = document.createElement("img");
  emoteElement.src = `temp-assets/emotes/${emotePath}`;
  emoteElement.alt = emotePath;
  emoteElement.classList.add("emote");
  chatMessages.appendChild(emoteElement);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * Updates the text of the hint text element depending on the current game state.
 *
 * If there is only one player, it shows a message indicating that the game is waiting for more players.
 * If the player is the drawer, it shows the full word.
 * If the player has found the word, it shows a message indicating that the word has been found.
 * Otherwise, it shows a message asking the player to guess the word.
 */
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

/**
 * Starts the game timer.
 *
 * Initializes the remaining time to the game duration, removes the "not-started" class from the timer progress bar,
 * and calls updateTimerDisplay.
 *
 * Then, every second, it updates the remaining time by subtracting the elapsed seconds since the game start time.
 * It calls updateTimerDisplay with the updated remaining time.
 *
 * If the remaining time reaches 0, it clears the interval and calls handleGameEnd.
 */
function startGameTimer() {
  remainingTime = gameConfig.gameDuration;
  timerProgress.classList.remove("not-started");
  updateTimerDisplay();

  const timerInterval = setInterval(() => {
    const now = new Date();
    const elapsedSeconds = ((now - gameStartTime) / 1000).toFixed(0);
    remainingTime = Math.max(0, gameConfig.gameDuration - elapsedSeconds);

    updateTimerDisplay();

    if (remainingTime == 0) {
      clearInterval(timerInterval);
      handleGameEnd();
    }
  }, 1000);
}

/**
 * Updates the display of the timer in the game section.
 *
 * It updates the text of the timer to show the remaining time in minutes and seconds.
 * It also updates the width of the progress bar to represent the remaining time.
 * Finally, it changes the color of the timer text to red if the remaining time is below 30% of the game duration.
 */
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

/**
 * Handles the end of the game.
 *
 * Clears the canvas, and if the current player is the drawer, it sends a "game_finished" event to the server.
 */
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

/**
 * Sends a new message to the server.
 *
 * The message is sent as a JSON object containing the message itself, the player's ID, pseudo, and remaining time.
 * The message is only sent if it is not empty.
 *
 * @param {string} message - The message to be sent.
 */
function sendMessage(message) {
  if (message) {
    socket.send(
      JSON.stringify({
        header: "new_message",
        type: "guess",
        pid: myId,
        pseudo: pseudo,
        message: message,
        remaining_time: remainingTime,
      })
    );
  }
}

/**
 * Handles the end of the game.
 *
 * Clears the canvas, and if the current player is the drawer, it sends a "game_finished" event to the server.
 */
function handleGameEnd() {
  clearCanvas();
  if (myId == drawerId) {
    socket.send(
      JSON.stringify({
        header: "game_finished",
      })
    );
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
    console.log(typeof allFrames);
    allFrames.push(frame);

    console.log(pos);
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

/**
 * Simplifies a list of frames by removing redundant color and radius properties.
 * Converts hex color values to RGB arrays for frames of type 'line'.
 *
 * @param {Array} frames - The array of frame objects to be processed. Each frame object should have a 'type' property and, if the type is 'line', may have 'color' and 'radius' properties.
 * @returns {Array} - The modified array of frames with redundant properties removed and hex colors converted to RGB.
 */

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
    Array.from(colorOptions)
      .find((option) => option.classList.contains("active"))
      .classList.remove("active");
    option.classList.add("active");
  });
});

sizeSlider.addEventListener("input", (event) => {
  drawingState.radius = parseInt(event.target.value);
});
