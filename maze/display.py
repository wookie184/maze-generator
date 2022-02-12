import subprocess
import tempfile
from colorsys import hsv_to_rgb
from pathlib import Path
from typing import Any, Iterator, List, Optional, Tuple

import pyglet
from PIL import Image
from pyglet import clock, shapes

from .constants import ColourInfo, MediaFormat, ReturnType, SaveOption, Size, Speed
from .helpers import MazeGenerator

WALL_COLOUR = (0, 0, 0)
SPACE_COLOUR = (255, 255, 255)


def colour_cycle(
    start: float = 0, incr: float = 0.01, *, s: float = 255, v: float = 255
) -> Iterator[Tuple[float, ...]]:
    """Return an iterator of smoothly changing rgb colours."""
    start, incr, s, v = start / 255, incr / 255, s / 255, v / 255
    h = start
    while True:
        h += incr
        h %= 1
        yield tuple(i * 255 for i in hsv_to_rgb(h, s, v))


class GridWindow(pyglet.window.Window):  # type:ignore[misc]
    def __init__(
        self,
        grid_size: Size,
        window_size: Size,
        colour_info: ColourInfo,
        speed: Speed,
        save_options: SaveOption,
        temp_dir: Optional[Path] = None,
    ):
        super().__init__(window_size.width, window_size.height)

        self.save_options = save_options
        if self.save_options.format == MediaFormat.GIF:
            self.gif_images: List[Image.Image] = []
        elif self.save_options.format == MediaFormat.MP4:
            self.mp4_frame = 0
            self.mp4_temp_dir = temp_dir

        self.shapes = {}
        self.shape_batch = shapes.Batch()

        self.grid_width = grid_size.width * 2 + 1
        self.grid_height = grid_size.height * 2 + 1

        square_height = self.height / self.grid_height
        square_width = self.width / self.grid_width

        for grid_x in range(self.grid_width):
            for grid_y in range(self.grid_height):
                square = shapes.Rectangle(
                    x=grid_x * square_width,
                    y=grid_y * square_height,
                    width=square_width,
                    height=square_height,
                    color=SPACE_COLOUR,
                    batch=self.shape_batch,
                )
                self.shapes[grid_x, grid_y] = square

        self.grid = MazeGenerator(self.grid_width, self.grid_height)

        self.pos_colour = colour_cycle(start=colour_info.start, incr=colour_info.speed)

        self.speed = speed
        self.draw_maze()
        self.on_draw()

        if self.save_options.format or self.speed.frames_per_second == -1:
            clock.schedule(self.on_tick)
        else:
            clock.schedule_interval(self.on_tick, 1 / self.speed.frames_per_second)

    def draw_maze(self) -> None:
        for shape in self.shapes.values():
            shape.color = SPACE_COLOUR

        # Fixed walls
        for grid_x in range(1, self.grid_width // 2 + 1):
            for grid_y in range(1, self.grid_height // 2 + 1):
                self.shapes[grid_x * 2 - 1, grid_y * 2 - 1].color = WALL_COLOUR

        # Optional walls
        for edge in self.grid.walls:
            self.shapes[edge].color = WALL_COLOUR

    def on_tick(self, _dt: int) -> None:
        for _ in range(self.speed.steps_per_frame):
            res = self.grid.step()
            if res == ReturnType.COMPLETED:
                if self.save_options.format:
                    self.on_draw()  # Ensure last frame is encluded
                    self.save_result()
                    pyglet.app.exit()
                    break
            elif res.type == ReturnType.BACKTRACK:
                pos, wall, nxt = res.value
                self.shapes[pos].color = next(self.pos_colour)
                self.shapes[wall].color = next(self.pos_colour)
            elif res.type == ReturnType.NEW:
                pos, wall, nxt = res.value
                self.shapes[pos].color = next(self.pos_colour)
                self.shapes[wall].color = next(self.pos_colour)
                self.shapes[nxt].color = next(self.pos_colour)

    def on_draw(self) -> None:
        self.clear()
        self.shape_batch.draw()

        if self.save_options.format == MediaFormat.MP4:
            pyglet.image.get_buffer_manager().get_color_buffer().save(
                f"{self.mp4_temp_dir}/{self.mp4_frame}.png"
            )
            self.mp4_frame += 1
        elif self.save_options.format == MediaFormat.GIF:
            self.gif_images.append(
                Image.frombytes(
                    "RGBA",
                    (self.width, self.height),
                    pyglet.image.get_buffer_manager()
                    .get_color_buffer()
                    .get_image_data()
                    .get_data(),
                )
            )

    def save_result(self) -> None:
        if self.save_options.format == MediaFormat.MP4:
            # fmt: off
            subprocess.run(
                [
                    "ffmpeg",
                    "-framerate", str(self.speed.frames_per_second),
                    "-i", "%d.png",
                    "-c:v", "libx264",
                    "-crf", "10",
                    "-preset", "veryslow",
                    "-tune", "animation",
                    "-pix_fmt", "yuv420p",
                    "-r", "30",
                    str((Path.cwd() / "out.mp4").absolute()),
                ],
                cwd=self.mp4_temp_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            # fmt: on
        elif self.save_options.format == MediaFormat.GIF:
            duration = int((1 / self.speed.frames_per_second) * 1000)
            self.gif_images[0].save(
                "out.gif",
                save_all=True,
                append_images=self.gif_images[1:],
                duration=duration,
            )
        elif self.save_options.format == MediaFormat.PNG:
            self.get_screen_as_image().save(f"{self.save_options.path}.png")
        elif self.save_options.format == MediaFormat.JPEG:
            self.get_screen_as_image().convert("RGB").save(
                f"{self.save_options.path}.jpg", quality=99, optimize=True
            )

    def get_screen_as_image(self) -> Image.Image:
        return Image.frombytes(
            "RGBA",
            (self.width, self.height),
            pyglet.image.get_buffer_manager()
            .get_color_buffer()
            .get_image_data()
            .get_data(),
        )


def run(*, save_option: SaveOption, **kwargs: Any) -> None:
    if save_option.format == MediaFormat.MP4:
        with tempfile.TemporaryDirectory() as temp_dir:
            window = GridWindow(
                save_options=save_option, temp_dir=Path(temp_dir), **kwargs
            )
            pyglet.app.run()
    else:
        window = GridWindow(save_options=save_option, **kwargs)  # noqa: F841
        pyglet.app.run()
