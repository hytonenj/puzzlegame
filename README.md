# Puzzle Game

Welcome to the Puzzle Game! This is a fun and challenging game where you need to move the key to open a door to next level. 

## How to Play

- Use the `W`, `A`, `S`, `D` keys to move the player up, left, down, and right respectively.
- Use the `Z` key to undo the last movement.
- Use the `R` key to reset the current level.

## Prerequisites

- [Poetry](https://python-poetry.org/) - Dependency Management and Packaging tool for Python.


## Installation

1. Install Poetry:
    ```sh
    curl -sSL https://install.python-poetry.org | python3 -
    ```

2. Clone the repository:
    ```sh
    git clone https://github.com/hytonenj/puzzlegame.git
    cd puzzlegame
    ```

3. Install the required dependencies:
    ```sh
    poetry install
    ```

4. Run the game:
    ```sh
    poetry run python main.py
    ```