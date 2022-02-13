import pathlib

import click

from . import display
from .constants import Size


def add_options(options):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func

    return _add_options


def validate_size(value: str) -> Size:
    try:
        width, _, height = value.partition("x")
        width, height = int(width), int(height)
    except ValueError:
        raise click.BadParameter("Format must be WIDTHxHEIGHT, e.g. 100x50")

    return Size(width, height)


def validate_grid_size(ctx: click.Context, param: click.Parameter, value: str) -> Size:
    size = validate_size(value)
    if not (2 <= size.width <= 100 and 2 <= size.width <= 100):
        raise click.BadParameter("Grid height and with must be between 2 and 100")
    return size


def validate_window_size(
    ctx: click.Context, param: click.Parameter, value: str
) -> Size:
    size = validate_size(value)
    if size.width < 150 or size.height < 150:
        raise click.BadParameter("Window height and width must be greater than 150px")
    return size


MAZE_OPTIONS = [
    click.option(
        "--window-size",
        "-w",
        "window_size",
        default="700x600",
        callback=validate_window_size,
        help="Size of the window, e.g. 100x200",
    ),
    click.option(
        "--grid-size",
        "-g",
        "grid_size",
        default="10x10",
        callback=validate_grid_size,
        help="Dimensions of the grid, e.g. 10x10",
    ),
    click.option(
        "--colour-speed",
        "colour_speed",
        default=1,
        type=click.FloatRange(0, 255),
        help="Colour change as HSV hue per generation step",
    ),
    click.option(
        "--start-colour",
        "colour_start",
        default=0,
        type=click.IntRange(0, 255),
        help="The colour to start at as a HSV hue",
    ),
    click.option(
        "--step",
        "step",
        default=1,
        type=click.IntRange(1),
        help="Number of generation steps per frame",
    ),
]

SAVE_PATH_OPTION = click.option(
    "--save-path",
    "save_path",
    type=click.Path(
        exists=False,
        dir_okay=False,
        writable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    default=pathlib.Path.cwd().absolute() / "out",
    help="Path to save to",
)

DURATION_OPTION = click.option(
    "--duration",
    "-d",
    "frame_duration",
    default=100,
    type=click.IntRange(1),
    help="Duration between frames (ms)",
)


@click.group(invoke_without_command=True, context_settings={"max_content_width": 95})
@add_options(MAZE_OPTIONS)
@DURATION_OPTION
@click.pass_context
@click.help_option("--help", "-h")
def maze(ctx, **kwargs):
    if ctx.invoked_subcommand is None:
        display.run(**kwargs)


@maze.command()
@add_options(MAZE_OPTIONS)
@SAVE_PATH_OPTION
@DURATION_OPTION
def gif(**kwargs):
    display.save_gif(**kwargs)


@maze.command()
@add_options(MAZE_OPTIONS)
@SAVE_PATH_OPTION
def png(save_path, **kwargs):
    display.save_image(save_path=save_path.with_suffix(".png"), **kwargs)


@maze.command()
@add_options(MAZE_OPTIONS)
@SAVE_PATH_OPTION
def bmp(save_path, **kwargs):
    display.save_image(save_path=save_path.with_suffix(".bmp"), **kwargs)
