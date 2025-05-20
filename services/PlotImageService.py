from io import BytesIO
from typing import Tuple, List

import numpy
from PIL import Image, ImageDraw

from data.PlotterInstruction import PlotterInstruction
from data.Vector import Vector


class PlotImageService:

    def __init__(self):
        self.outline_color = (51,51,255,255)
        self.region_color = (33,33,33,255)
        self.connections_color = (255,255,102,255)
        self.ms_frame_delay = 5000

    def plot_image(self, original_image : Image, plotter_instructions : PlotterInstruction) -> List[Image]:
        frames = []
        image_dims = self.get_image_dimensions(plotter_instructions)

        frames.append(self._draw_regions(image_dims, plotter_instructions))
        frames.append(self._draw_outlines(image_dims,plotter_instructions))
        frames.append(self._draw_connecting_paths(image_dims,plotter_instructions))
        return frames

    def draw_animated_path(self, starting_img : Image, steps_per_frame: int, plotter_instructions : PlotterInstruction) -> List[Image]:
        frames = []
        max_steps = len(plotter_instructions.absolute_position_path)
        draw = ImageDraw.Draw(starting_img)
        for step_index in range(0, max_steps, steps_per_frame):

            # draw steps for current frame
            last_index = min(step_index + steps_per_frame, max_steps - 1)
            for i in range(step_index, last_index):
                pixel_coord = plotter_instructions.absolute_position_path[i]
                draw.point((pixel_coord.x, pixel_coord.y), (0, 0, 0, 255))

            # create copy to render stylus tracker for current frame
            img_with_stylus_tracking = starting_img.copy()
            img_with_stylus_tracking_draw = ImageDraw.Draw(img_with_stylus_tracking)

            # render stylus tracker pixel
            if last_index < max_steps:
                pixel_coord = plotter_instructions.absolute_position_path[last_index]
                img_with_stylus_tracking_draw.point((pixel_coord.x, pixel_coord.y), (255, 0, 0, 255))

            # save current snapshot
            frames.append(img_with_stylus_tracking)

        return frames

    def to_gif(self, frames : List[Image], durations : List[int]) -> BytesIO:
        buffer = BytesIO()
        if len(durations) != len(frames):
            raise ValueError("Length of durations list must match number of frames")

        frames[0].save(buffer, format='GIF', save_all=True, append_images=frames[1:],  duration=durations, loop=0)
        gif_data = buffer.getvalue()
        return BytesIO(gif_data)

    def _draw_regions(self, image_dims : Tuple[int,int],plotter_instructions : PlotterInstruction, img : Image = None) -> Image:
        if img is None:
            img = Image.new('RGB', image_dims, 'white')

        draw = ImageDraw.Draw(img)

        for region in plotter_instructions.regions:
            for vector in region.region:
                draw.point((vector.x, vector.y), self.region_color)
        return img

    def _draw_outlines(self, image_dims : Tuple[int,int],plotter_instructions : PlotterInstruction, img : Image = None) -> Image:
        if img is None:
            img = Image.new('RGB', image_dims, 'white')

        self._draw_regions(image_dims, plotter_instructions, img)

        draw = ImageDraw.Draw(img)

        for outline in plotter_instructions.region_outlines:
            for vector in outline:
                draw.point((vector.x,vector.y), self.outline_color)
        return img

    def _draw_connecting_paths(self,image_dims : Tuple[int,int],plotter_instructions : PlotterInstruction, img : Image = None) -> Image:
        img = self._draw_outlines(image_dims, plotter_instructions, img)
        if img is None:
            img = Image.new('RGB', image_dims, 'white')

        self._draw_regions(image_dims, plotter_instructions, img)
        self._draw_outlines(image_dims, plotter_instructions, img)
        draw = ImageDraw.Draw(img)

        for path in plotter_instructions.connecting_paths:
            for vector in path:
                draw.point((vector.x,vector.y), self.connections_color)
        return img

    def get_image_dimensions(self, plotter_instructions: PlotterInstruction) -> Tuple[int, int]:
        bounding_rect = self.get_bounding_rect_from_instructions(plotter_instructions)
        border_width = bounding_rect[0]
        border_height = bounding_rect[1]
        return (bounding_rect[2]+border_width*2,
                bounding_rect[3]+border_height*2)

    @staticmethod
    def get_bounding_rect_from_instructions(plotter_instructions : PlotterInstruction) -> Tuple[int, int, int, int]:
        max_x = 0
        max_y = 0
        min_x = numpy.inf
        min_y = numpy.inf
        for outline in plotter_instructions.region_outlines:
            for vector in outline:

                max_x = max(vector.x, max_x)
                max_y = max(vector.y, max_y)

                min_x = min(vector.x, min_x)
                min_y = min(vector.y, min_y)
        return min_x, min_y, max_x-min_x, max_y-min_y