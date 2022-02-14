# Maze Generator

An a-maze-ing maze generator :)

Has support for viewing generation in a window using pyglet, or saving as a GIF. You can also save the final image as a PNG or BMP!

![GIF of colourful maze being generated](https://github.com/wookie184/maze-generator/blob/main/examples/out.gif)


### Usage
Usage: python -m maze [OPTIONS] COMMAND [ARGS]...

Options:
  -w, --window-size TEXT        Size of the window, e.g.
                                100x200
  -g, --grid-size TEXT          Dimensions of the grid, e.g.
                                10x10
  --colour-speed FLOAT RANGE    Colour change as HSV hue per
                                generation step  [0<=x<=255]
  --start-colour INTEGER RANGE  The colour to start at as a
                                HSV hue  [0<=x<=255]
  --seed INTEGER                A seed to determine the maze
                                generated
  --help                        Show this message and exit.

Commands:
  bmp   Save a BMP of a generated maze.
  gif   Save an animated GIF of a maze generating.
  png   Save a PNG of a generated maze.
  view  Open a window to show a maze generating.


Command specific options can be found by running the help commands for the respective command.

### Contributing

This project uses poetry for dependency management and also uses precommit.

To set it up locally:
1) Clone the project `git clone https://github.com/wookie184/maze-generator.git`
2) Ensure you are in the root directory and run `poetry install`
3) Install the precommit hooks using `poetry run poe precommit` or just `poe precommit` if the poetry environment is activated
