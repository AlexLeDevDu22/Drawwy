// Configuration
const gameConfig = {
    gameDuration: 120, // seconds
    canvasWidth: 800,
    canvasHeight: 600,
    serverUrl: "wss://vital-mastiff-publicly.ngrok-free.app"
};

// Game state
let gameState = {
    playerId: null,
    players: [],
    drawerId: null,
    isDrawing: false,
    currentSentence: "",
    gameStartTime: null,
    remainingTime: gameConfig.gameDuration,
    hasFound: false,
    messages: [],
    allFrames: []
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
    undoStack: []
};

// DOM elements
const loginOverlay = document.getElementById('login-overlay');
const loginForm = document.getElementById('login-form');
const avatarSelection = document.getElementById('avatar-selection');
const avatarOptions = document.querySelectorAll('.avatar-option');
const playerList = document.getElementById('player-list');
const wordDisplay = document.getElementById('word-display');
const hintText = document.getElementById('hint-text');
const timerText = document.getElementById('timer-text');
const timerProgress = document.getElementById('timer-progress');
const canvas = document.getElementById('drawing-canvas');
const ctx = canvas.getContext('2d');
const toolButtons = document.querySelectorAll('.tool-btn');
const colorOptions = document.querySelectorAll('.color-option');
const sizeSlider = document.getElementById('size-slider');
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const drawingTools = document.getElementById('drawing-tools');
const gameModal = document.getElementById('game-modal');
const resultInfo = document.getElementById('result-info');
const wordReveal = document.getElementById('word-reveal');
const continueBtn = document.getElementById('continue-btn');

// WebSocket connection
let socket = null;

// Initialize the canvas
function initCanvas() {
    // Set canvas size
    canvas.width = canvas.offsetWidth;
    canvas.height = 400;
    
    // Clear the canvas
    ctx.fillStyle = "#FFFFFF";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
}

// Handle WebSocket connection
function connectToServer(pseudo, avatar) {
    socket = new WebSocket(gameConfig.serverUrl);

    socket.onopen = function() {
        console.log("Connected to server");
        // Send join request
        socket.send(JSON.stringify({
            type: "join",
            pseudo: pseudo,
            avatar: avatar
        }));
    };

    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        console.log("Received message:", data);

        switch(data.type) {
            case "welcome":
                handleWelcome(data);
                break;
            case "new_player":
                handleNewPlayer(data);
                break;
            case "update":
                handleUpdate(data);
                break;
            default:
                console.log("Unknown message type:", data.type);
        }
    };

    socket.onclose = function() {
        console.log("Connection closed");
        addSystemMessage("Connexion au serveur perdue. Rechargez la page pour vous reconnecter.");
    };

    socket.onerror = function(error) {
        console.error("WebSocket error:", error);
        addSystemMessage("Erreur de connexion au serveur.");
    };
}

// Handle welcome message
function handleWelcome(data) {
    gameState.playerId = data.id;
    gameState.players = data.players;
    gameState.messages = data.messages || [];
    
    // Update player list
    updatePlayerList();
    
    // Add messages to chat
    if (gameState.messages.length > 0) {
        clearChat();
        gameState.messages.forEach(message => {
            addMessageToChat(message);
        });
    }
    
    // Set game start time if provided
    if (data.new_game) {
        gameState.gameStartTime = new Date(data.new_game);
        startGameTimer();
    }
    
    addSystemMessage(`Bienvenue dans le jeu, ${getPlayerById(gameState.playerId).pseudo} !`);
}

// Handle new player message
function handleNewPlayer(data) {
    gameState.players.push(data.player);
    updatePlayerList();
    addSystemMessage(`${data.player.pseudo} a rejoint la partie !`);
}

// Handle update message
function handleUpdate(data) {
    // Update drawer ID
    gameState.drawerId = data.drawer_id;
    
    // Update drawing if we're not the drawer
    if (data.frames && gameState.playerId !== gameState.drawerId) {
        updateCanvas(data.frames);
    }
    
    // Update current sentence
    if (data.sentence) {
        gameState.currentSentence = data.sentence;
        updateWordDisplay();
    }
    
    // Add new message if provided
    if (data.new_message) {
        addMessageToChat(data.new_message);
        
        // If this player found the word
        if (data.new_message.player_id === gameState.playerId && data.new_message.succeed) {
            gameState.hasFound = true;
            updatePlayerList(); // Update UI to show found status
        }
    }
    
    // Handle new game
    if (data.new_game) {
        gameState.gameStartTime = new Date(data.new_game);
        gameState.hasFound = false;
        
        // Clear the canvas
        initCanvas();
        gameState.allFrames = [];
        
        // Reset drawing state
        drawingState.frames = [];
        drawingState.currentStep = 0;
        drawingState.undoStack = [];
        
        // Update UI elements
        updatePlayerList();
        updateWordDisplay();
        
        // Start the timer
        startGameTimer();
        
        addSystemMessage(`Nouvelle partie ! C'est le tour de ${getPlayerById(gameState.drawerId).pseudo}`);
        
        // If this player is the drawer, enable drawing tools
        toggleDrawingTools();
    }
    
    // Update player list to reflect current state
    updatePlayerList();
}

// Update player list UI
function updatePlayerList() {
    playerList.innerHTML = '';
    
    gameState.players.forEach(player => {
        const playerItem = document.createElement('li');
        playerItem.className = 'player-item';
        
        // Add classes based on player status
        if (player.id === gameState.drawerId) {
            playerItem.classList.add('current-drawer');
        }
        
        if (player.found) {
            playerItem.classList.add('found');
        }
        
        const avatarBg = getAvatarBackground(player.avatar);
        
        playerItem.innerHTML = `
            <div class="avatar" style="background-color: ${avatarBg}">
                ${player.avatar || '👤'}
            </div>
            <div class="player-info">
                <div class="player-name">${player.pseudo}${player.id === gameState.playerId ? ' (Vous)' : ''}</div>
                <div class="player-score">${player.points} points</div>
            </div>
            <div>
                ${player.id === gameState.drawerId ? 
                    '<span class="player-status status-drawing">Dessine</span>' : ''}
                ${player.found ? 
                    '<span class="player-status status-found">Trouvé !</span>' : ''}
            </div>
        `;
        
        playerList.appendChild(playerItem);
    });
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
        const hint = firstLetter + '_'.repeat(gameState.currentSentence.length - 1);
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
        gameState.remainingTime = Math.max(0, gameConfig.gameDuration - elapsedSeconds);
        
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
    timerText.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
    
    // Update progress bar
    const progressPercent = (gameState.remainingTime / gameConfig.gameDuration) * 100;
    timerProgress.style.width = `${progressPercent}%`;
    
    // Change color as time runs out
    if (progressPercent < 30) {
        timerProgress.style.color="red";
    } else {
        timerProgress.style.color="#333";
    }
}