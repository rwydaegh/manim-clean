from manim import *
from manim_slides import Slide
import numpy as np

class RogueWavePlot(Slide):
    def construct(self):
        np.random.seed(0)

        # Create the wave function with randomness
        def wave_function(x):
            return 5 * ( 2 * np.cos(2 * np.pi * x) + 0.5 * np.cos(2.1 * np.pi * x) + 0.5 * np.cos(1.9 * np.pi * x) ) / 3 + 2 * np.random.rand() 

        # Define rogue wave in the middle
        def rogue_wave_function(x):
            return 20 * np.cos(2 * np.pi * (x - 5)) * np.exp(-((x - 5) ** 2/0.1))

        # Create the combined wave function
        def combined_wave_function(x):
            return wave_function(x) + rogue_wave_function(x)

        # Set up axes
        x_range = np.linspace(0, 10, 1000)
        x_min = np.min(x_range)
        x_max = np.max(x_range)
        y_min = np.min(combined_wave_function(x_range))
        y_max = np.max(combined_wave_function(x_range)) + 5
        axes = Axes(
            x_range=[x_min, x_max, 1],
            y_range=[y_min, y_max, 3],
            axis_config={
                "include_tip": True,
                "include_numbers": True,
                "color": WHITE,
            }
        )

        # add grid to axes
        axes.add_coordinates()

        self.add(axes)

        # Create the curve
        wave_curve = axes.plot(combined_wave_function, color=BLUE)

        # Add labels
        x_label = axes.get_x_axis_label(Tex("Time [s]").next_to(axes.x_axis, RIGHT))
        y_label = axes.get_y_axis_label(Tex("Wave size [m]").next_to(axes.y_axis, DOWN))

        # Dot at the maximum
        # Find the maximum point of the wave curve
        max_point_coords = [x_range[np.argmax(combined_wave_function(x_range))], np.max(combined_wave_function(x_range))]
        max_point_coords[1] += 1.5
        dot = Dot(axes.coords_to_point(max_point_coords[0], max_point_coords[1]), color=RED)
        lines = axes.get_lines_to_point(axes.c2p(max_point_coords[0], max_point_coords[1]))

        # Animate the creation of the wave curve
        self.play(Create(axes), Create(wave_curve), Write(x_label), Write(y_label), run_time = 3)
        self.play(Create(dot), Create(lines), run_time = 1)

        # Hold the final scene for a bit
        self.wait(0.5)

# To run this script, save it as a .py file and use the following command in the terminal:
# manim -pql your_script_name.py RogueWavePlot
