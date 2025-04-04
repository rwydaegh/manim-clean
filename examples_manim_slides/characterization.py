from manim import *
from manim_slides import Slide

class Characterization(Slide):
    def construct(self):
        # Write characterization top of slide, small
        title = Tex(r"\underline{Characterization}")
        title.scale(0.7)
        title.shift(UP * 3.5)

        self.play(Write(title), run_time=1)

        self.wait(0.5)
        self.next_slide()

        # Left enumerate with math symbols
        left_enum = Tex(
            r'''
            \begin{enumerate}
            \item Peak
            \item FWHM, \(\forall\) dimensions
            \item Peak-to-prominence ratio
            \item Dimensionality
            \item Ellipticity
            \item Mean background field
            \end{enumerate}'''
        )
        left_enum.shift(LEFT * 3.9)

        # Right enumerate with math symbols
        right_enum = Tex(
            r'''
            \begin{enumerate}
            \setcounter{enumi}{6}
            \item Peak-to-background ratio
            \item Side-lobe peaks, \(\forall\) orders
            \item Side-lobe distances, \(\forall\) orders
            \item Troughs depths, \(\forall\) orders
            \item Troughs distances, \(\forall\) orders
            \item Side-lobe-peak ratios
            \end{enumerate}'''
        )
        right_enum.shift(RIGHT * 3.5)

        self.play(Write(left_enum), Write(right_enum), run_time=1)

        self.wait(0.5)
        self.next_slide()