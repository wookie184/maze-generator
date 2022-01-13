import pathlib
from typing import Optional

import click

from . import display
from .constants import ColourInfo, MediaFormat, SaveOption, Size, Speed


def to_mediaformat(
    ctx: click.Context, param: click.Parameter, value: Optional[str]
) -> Optional[MediaFormat]:
    if value is None:
        return None

    return MediaFormat.from_string(value)


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


@click.command("Maze Generator", context_settings={"max_content_width": 110})
@click.option(
    "--grid-size",
    "-g",
    default="10x10",
    callback=validate_grid_size,
    help="The dimensions of the maze grid, e.g. 10x10",
)
@click.option(
    "--window-size",
    "-w",
    default="700x600",
    callback=validate_window_size,
    help="The resolution of the window, e.g. 100x200",
)
@click.option(
    "--colour-speed",
    "-c",
    default=10,
    help="The speed the colour changes. Enter 0 for no colour change",
)
@click.option(
    "--start-colour",
    default=0,
    help="The colour to start at, given as a HSV hue between 0 and 255",
)
@click.option(
    "--frames-per-second",
    "-fps",
    default=20,
    help="Number of updates per second to aim for",
)
@click.option(
    "--steps-per-frame", "-spf", default=1, help="Number of steps to make per frame"
)
@click.option(
    "--save-format",
    type=click.Choice(MediaFormat.formats(), case_sensitive=False),
    callback=to_mediaformat,
    default=None,
    show_default=True,
    help=(
        "Save the maze generation in the format passed. Nothing is saved by default. "
        "Video formats will save an animation, while image formats save the final frame. "
        "Using this option will run the live animation at maximum speed, and the -fps argument "
        "will be used for the video fps"
    ),
)
@click.option(
    "--save-path",
    type=click.Path(
        exists=False,
        dir_okay=False,
        writable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    default=pathlib.Path.cwd().absolute() / "out",
    help="Choose path to save ",
)
@click.help_option("--help", "-h")
def maze_generator(
    grid_size: Size,
    window_size: Size,
    colour_speed: float,
    start_colour: int,
    frames_per_second: int,
    steps_per_frame: int,
    save_format: MediaFormat,
    save_path: pathlib.Path,
) -> None:

    colour_speed = 1 / colour_speed
    display.run(
        grid_size=grid_size,
        window_size=window_size,
        colour_info=ColourInfo(start=start_colour, speed=colour_speed),
        save_option=SaveOption(format=save_format, path=save_path),
        speed=Speed(
            frames_per_second=frames_per_second, steps_per_frame=steps_per_frame
        ),
    )
