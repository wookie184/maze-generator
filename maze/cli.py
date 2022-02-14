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


def validate_size(
    ctx: click.Context, param: click.Parameter, value: str
) -> Size:
    try:
        width, _, height = value.partition("x")
        width, height = int(width), int(height)
    except ValueError:
        raise click.BadParameter("Format must be WIDTHxHEIGHT, e.g. 100x50")

    if not (2 <= width and 2 <= width):
        raise click.BadParameter("height and width must be greater than 1")
    return Size(width, height)


MAZE_OPTIONS = [
    click.option(
        "--window-size",
        "-w",
        "window_size",
        default="620x620",
        callback=validate_size,
        help="Size of the window, e.g. 100x200",
    ),
    click.option(
        "--grid-size",
        "-g",
        "grid_size",
        default="15x15",
        callback=validate_size,
        help="Dimensions of the grid, e.g. 10x10",
    ),
    click.option(
        "--colour-speed",
        "colour_speed",
        default=0.5,
        type=click.FloatRange(0, 255),
        help="Colour change as HSV hue per generation step",
    ),
    click.option(
        "--start-colour",
        "colour_start",
        default=100,
        type=click.IntRange(0, 255),
        help="The colour to start at as a HSV hue",
    ),
    click.option(
        "--seed",
        "seed",
        default=-1,
        help="A seed to determine the maze generated",
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

ANIMATION_OPTIONS = [
    click.option(
        "--duration",
        "-d",
        "frame_duration",
        default=40,
        type=click.IntRange(1),
        help="Duration between frames (ms)",
    ),
    click.option(
        "--step",
        "step",
        default=1,
        type=click.IntRange(1),
        help="Number of generation steps per frame",
    ),
]


@click.group(context_settings={"max_content_width": 95})
@add_options(MAZE_OPTIONS)
@click.pass_context
def maze(ctx, window_size, grid_size, **kwargs):
    if grid_size.width * 2 + 1 > window_size.width:
        raise click.BadParameter(
            "window/image width is too small for that grid width"
        )
    if grid_size.height * 2 + 1 > window_size.height:
        raise click.BadParameter(
            "window/image height is too small for that grid height"
        )

    if (
        window_size.width % (grid_size.width * 2 + 1) != 0
        or window_size.height % (grid_size.height * 2 + 1) != 0
    ):
        click.echo(
            "Note: It is recommended that window size "
            "is a multiple of 2*grid_size+1"
        )

    ctx.obj = {"window_size": window_size, "grid_size": grid_size, **kwargs}


@maze.command()
@add_options(ANIMATION_OPTIONS)
@click.pass_context
def view(ctx, **kwargs):
    window_size = ctx.obj["window_size"]
    if window_size.width < 150 or window_size.height < 150:
        raise click.BadParameter(
            "Window height and width must be greater than 150px"
        )
    display.run(**ctx.obj, **kwargs)


@maze.command()
@add_options(ANIMATION_OPTIONS)
@SAVE_PATH_OPTION
@click.pass_context
def gif(ctx, save_path, **kwargs):
    display.save_gif(save_path, **ctx.obj, **kwargs)
    click.echo(f"GIF created at {save_path}")


@maze.command()
@SAVE_PATH_OPTION
@click.pass_context
def png(ctx, save_path, **kwargs):
    save_path = save_path.with_suffix(".png")
    display.save_image(
        save_path,
        step=100_000,
        **ctx.obj,
        **kwargs,
    )
    click.echo(f"PNG created at {save_path}")


@maze.command()
@SAVE_PATH_OPTION
@click.pass_context
def bmp(ctx, save_path, **kwargs):
    save_path = save_path.with_suffix(".bmp")
    display.save_image(
        save_path,
        step=100_000,
        **ctx.obj,
        **kwargs,
    )
    click.echo(f"BMP created at {save_path}")
