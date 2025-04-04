from manim import *  # or: from manimlib import *

from manim_slides import Slide


class BasicExample(Slide):
    def construct(self):
        # make E=mc2 appear
        formula = MathTex("E=mc^2")
        self.play(Write(formula))
        self.next_slide()