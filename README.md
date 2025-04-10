# Game of Life (GOL)

Welcome to the **Game of Life**! This README will guide you through the installation process and explain how to play the game.

## Installation

1. **Clone the Repository**  
    Open your terminal and run:
    ```bash
    git clone https://github.com/shadi-danhash/game-of-life.git
    cd game-of-life
    ```

2. **Install Dependencies**  
    Ensure you have the required dependencies installed. If the game uses Python, for example:
    ```bash
    pip install -r requirements.txt
    ```

3. **Run the Game**  
    Start the game server by executing:
    ```bash
    python3 backend/socket_server.py
    ```

    Then open the `frontend/index.html` file

## How to Play

1. **Game Rules**  
    - The game is played on a grid of cells.
    - Each cell can be either alive or dead.
    - The state of each cell evolves based on the following rules:
      - A live cell with 2 or 3 live neighbors survives.
      - A dead cell with exactly 3 live neighbors becomes alive.
      - All other cells die or remain dead.

2. **Controls**  
    - Use the keyboard or mouse (if applicable) to interact with the game.
    - Press `Start` to begin the simulation.
    - Press `Pause` to stop the simulation and resers.
    - Use `Zoom in` and `Zoom out` to customize the grid size.

Enjoy exploring the fascinating patterns of the Game of Life!