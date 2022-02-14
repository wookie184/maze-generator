from colorsys import hsv_to_rgb
from pathlib import Path
from typing import Iterator, List, Tuple

import pyglet
from PIL import Image
from pyglet import clock, shapes

from .constants import ReturnType, Size
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
        colour_start: int,
        colour_speed: int,
        step: int,
        seed: int,
        visible: bool = True,
    ):
        super().__init__(
            window_size.width, window_size.height, visible=visible
        )

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

        self.grid = MazeGenerator(self.grid_width, self.grid_height, seed=seed)

        self.pos_colour = colour_cycle(start=colour_start, incr=colour_speed)
        self.step = step

        self.draw_maze()

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
        for _ in range(self.step):
            res = self.grid.step()
            if res == ReturnType.COMPLETED:
                self.on_finish()
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

    def on_finish(self):
        pass

    def get_screen_as_image(self) -> Image.Image:
        return Image.frombytes(
            "RGBA",
            (self.width, self.height),
            pyglet.image.get_buffer_manager()
            .get_color_buffer()
            .get_image_data()
            .get_data(),
        )

    def on_draw(self) -> None:
        self.clear()
        self.shape_batch.draw()


class GIFGridWindow(GridWindow):
    def __init__(self, save_path: Path, frame_duration: int, *args, **kwargs):
        super().__init__(*args, **kwargs, visible=False)
        self.gif_images: List[Image.Image] = []
        self.save_path = save_path
        self.frame_duration = frame_duration

    def on_tick(self, dt: int) -> None:
        super().on_tick(dt)
        self.on_draw()
        self.gif_images.append(self.get_screen_as_image())

    def on_finish(self):
        # Ensure the last frame is included
        self.on_draw()
        self.gif_images.append(self.get_screen_as_image())

        # Sleep for 2 seconds at the end before looping
        durations = [self.frame_duration] * (len(self.gif_images) - 1) + [2000]
        self.gif_images[0].save(
            self.save_path.with_suffix(".gif"),
            save_all=True,
            append_images=self.gif_images[1:],
            duration=durations,
            loop=0,
        )
        pyglet.app.exit()


class ImageGridWindow(GridWindow):
    def __init__(self, save_path: Path, *args, **kwargs):
        super().__init__(*args, **kwargs, visible=False)
        self.save_path = save_path

    def on_finish(self):
        self.on_draw()  # Ensure last frame is included
        self.get_screen_as_image().convert("RGB").save(
            self.save_path,
        )
        pyglet.app.exit()


def run(frame_duration: int, *args, **kwargs) -> None:
    window = GridWindow(*args, **kwargs)
    clock.schedule_interval(window.on_tick, frame_duration / 1000)
    pyglet.app.run()


def save_image(save_path: Path, *args, **kwargs) -> None:
    window = ImageGridWindow(save_path, *args, **kwargs)
    clock.schedule(window.on_tick)
    pyglet.app.run()


def save_gif(save_path: Path, frame_duration: int, *args, **kwargs):
    window = GIFGridWindow(save_path, frame_duration, *args, **kwargs)
    clock.schedule(window.on_tick)
    pyglet.app.run()
