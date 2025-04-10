// This is the main JavaScript file for the Game of Life application
// It handles the socket connection, game state management, and UI interactions

// ------------- UI Utils -------------
function setCanvasDimenssions() {
    const canvasWidth = window.innerWidth - 50; 
    const canvasHeight = window.innerHeight - 100;
    canvas.width = canvasWidth;
    canvas.height = canvasHeight;
}

function drawState(newCells) {
    if (newCells) {
        activeCells = newCells;
    }
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const startX = -Math.floor(canvas.width / gridSize / 2);
    const endX = Math.floor(canvas.width / gridSize / 2);
    const startY = -Math.floor(canvas.height / gridSize / 2);
    const endY = Math.floor(canvas.height / gridSize / 2);
    for (let x = startX; x <= endX; x++) {
        for (let y = startY; y <= endY; y++) {
            const isActive = activeCells.some(cell => cell[0] === x && cell[1] === y);
            ctx.fillStyle = isActive ? "#000" : "#f0f0f0"; 
            ctx.fillRect((x + Math.floor(canvas.width / (2 * gridSize))) * gridSize, 
                         (y + Math.floor(canvas.height / (2 * gridSize))) * gridSize, 
                         gridSize, gridSize);
            ctx.strokeStyle = '#999';
            ctx.lineWidth = 1;
            ctx.setLineDash([5, 3]);
            ctx.strokeRect((x + Math.floor(canvas.width / (2 * gridSize))) * gridSize, 
                           (y + Math.floor(canvas.height / (2 * gridSize))) * gridSize, 
                           gridSize, gridSize);
        }
    }
}


function zoomIn(){
    if (gridSize < 50) {
        gridSize += 5;
        drawState();
    }
}

function zoomOut(){
    if (gridSize > 5) {
        gridSize -= 5;
        drawState();
    }
}

// ------------- Game Controls -------------
function proceedToGame() {
    const mode = gameMode.value;
    const name = gameNameInput.value.trim();

    if ((mode === "new" || mode === "file") && !name) {
        alert("Please enter a game name.");
        return;
    }

    if (mode === "new") {
        socket.emit('new_game', { name });
    } else if (mode === "file") {
        const fileInput = document.getElementById("fileInput");
        if (!fileInput.files.length) {
            alert("Please select a file to load.");
            return;
        }

        const file = fileInput.files[0];
        parseLifFile(file)
            .then(data => {
                console.log('Parsed data:', data);
                socket.emit('new_game', { name, board_actives: data.board_actives });
            })
            .catch(error => {
                alert(`Error: ${error}`);
            });
    } else if (mode === "saved") {
        const game_id = savedGamesSelect.value;
        socket.emit('load_game', { game_id });
    }
}

function enterGame(boardActives) {
    setCanvasDimenssions();

    selectionUI.style.display = "none";
    gameControls.style.display = "block";
    canvas.style.display = "block";
    console.log('Entering game mode with active cells:', boardActives);
    activeCells = boardActives;
    drawState();
}

function startGame() {
    if (!isRunning) {
        document.getElementById('startGameBtn').disabled = true;
        isRunning = true;
        intervalId = setInterval(() => {
            socket.emit('play_move', {});
        }, MOVE_INTERVAL_MS);
    }
}

function stopGame() {
    isRunning = false;
    clearInterval(intervalId); 
    document.getElementById('startGameBtn').disabled = false;
    socket.emit('stop', {});
}

// ------------- Data IO -------------
function parseLifFile(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = function(event) {
            const content = event.target.result;
            const data = parseLifContent(content);
            if (data) {
                resolve(data);
            } else {
                reject('Corrupted or unsupported file format.');
            }
        };

        reader.onerror = function() {
            reject('Failed to read the file.');
        };

        reader.readAsText(file); 
    });
}

function parseLifContent(content) {
    const lines = content.split('\n');
    const activeCells = [];

    try {
        const dataStartIndex = lines.findIndex(line => line.startsWith('#Life 1.06'));
        if (dataStartIndex === -1) throw new Error('Invalid file structure.');
        for (let i = dataStartIndex + 1; i < lines.length; i++) {
            const line = lines[i].trim();
            if (line === '') continue;
            const parts = line.split(/\s+/);
            if (parts.length >= 2) {
                const x = parseInt(parts[0], 10);
                const y = parseInt(parts[1], 10);
                activeCells.push([x, y]);
            }
        }
        return { board_actives: activeCells };
    } catch (error) {
        return null;
    }
}

// ------------- Event Listeners and globals -------------

const socket = io('http://localhost:8000');

const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
let gridSize = 20;
let activeCells = [];
let isRunning = false;
let intervalId = null;
const MOVE_INTERVAL_MS = 500; 
// GUI Elements
const selectionUI = document.getElementById("selectionUI");
const gameControls = document.getElementById("gameControls");
const gameMode = document.getElementById("gameMode");
const nameInputDiv = document.getElementById("nameInputDiv");
const gameNameInput = document.getElementById("gameName");
const savedGamesDiv = document.getElementById("savedGamesDiv");
const savedGamesSelect = document.getElementById("savedGames");
selectionUI.style.display = "block";
gameControls.style.display = "none";
canvas.style.display = "none";
savedGamesDiv.style.display = "none"; 


gameMode.addEventListener("change", () => {
    const mode = gameMode.value;
    nameInputDiv.style.display = (mode === "new" || mode === "file") ? "block" : "none";
    savedGamesDiv.style.display = (mode === "saved") ? "block" : "none";
    if (mode === "saved") {
        socket.emit('get_all_games', {}); 
    }
    document.getElementById("fileInputDiv").style.display = (mode === "file") ? "block" : "none";
});


canvas.addEventListener('click', function (event) {
    if (isRunning) return; // Disable editing while running
    
    const startX = -Math.floor(canvas.width / gridSize / 2);  // Left-most cell
    const startY = -Math.floor(canvas.height / gridSize / 2); // Top-most cell

    const x = Math.floor(event.offsetX / gridSize) + startX;
    const y = Math.floor(event.offsetY / gridSize) + startY;
    console.log('Canvas clicked at:', x, y);

    const point = [x, y];
    socket.emit('toggle_point', { point });
});



// Socket events
socket.on('saved_games_list', (data) => {
    savedGamesSelect.innerHTML = "";
    data.savedGames.forEach(name => {
        const opt = document.createElement("option");
        opt.value = name;
        opt.textContent = name;
        savedGamesSelect.appendChild(opt);
    });
});
socket.on('all_games_fetched', (data) => {
    console.log('All games fetched:', data);
    const savedGamesSelect = document.getElementById("savedGames");
    savedGamesSelect.innerHTML = "";
    if (data && data.games) {
        data.games.forEach(game => {
            const option = document.createElement("option");
            option.value = game.id;
            option.textContent = game.name;
            savedGamesSelect.appendChild(option);
        });
        savedGamesSelect.disabled = false;
        savedGamesSelect.style.display = "block";
    } else {
        savedGamesSelect.disabled = true;
        alert("No saved games found.");
    }
});
socket.on('game_created', (data) => enterGame(data.board_actives)); 
socket.on('game_loaded', (data) => enterGame(data.board_actives));
socket.on('played_move', (data) => drawState(data.board_actives));
socket.on('play_stopped', (data) => drawState(data.board_actives));
socket.on('point_toggeled', (data) => drawState(data.board_actives));
socket.on('game_locked', (data) => {alert(data.message)});
socket.on('error', (data) => {alert(data.message)});
socket.connect();
