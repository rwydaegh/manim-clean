from manim import *
from manim_slides import Slide

class VersionEnumeration(Slide):
    def construct(self):
        # Define initial text
        title_2018 = Tex(r"\textbf{Hybrid Ray-Tracing/FDTD @ 3.5 GHz}", color=WHITE).scale(0.7).to_edge(LEFT).shift(RIGHT * 2)
        year_2018 = Tex(r"\textbf{2019}", color=WHITE).scale(0.7).to_edge(RIGHT)
        
        # Group the text together
        group_2018 = VGroup(title_2018, year_2018)
        group_2018.shift(UP * 3)
        
        # Define the blue arrow
        arrow = Arrow(start=UP * 10 + LEFT * 6.5, end=LEFT * 6.5 + UP * (group_2018.get_bottom()[1] - 0.3), color=BLUE, stroke_width=15)
        
        # Display the first group and arrow
        self.play(Write(group_2018), Create(arrow), run_time=1)
        self.wait(0.5)
        self.next_slide()

        # Reduce opacity and display new text
        self.play(group_2018.animate.set_opacity(0.5))
        
        title_2022 = Tex(r"\textbf{Hybrid Ray-Tracing/FDTD @ 28 GHz}", color=WHITE).scale(0.7).to_edge(LEFT).shift(RIGHT * 2)
        year_2022 = Tex(r"\textbf{2022}", color=WHITE).scale(0.7).to_edge(RIGHT)
        group_2022 = VGroup(title_2022, year_2022)
        group_2022.shift(UP * 1)

        new_arrow_end = LEFT * 6.5 + UP * (group_2022.get_bottom()[1] - 0.3)
        new_arrow = Arrow(start=arrow.get_start(), end=new_arrow_end, color=BLUE, stroke_width=15)
        
        self.play(Write(group_2022), Transform(arrow, new_arrow), run_time=1)
        self.wait(0.5)
        self.next_slide()

        # Reduce opacity and display new text
        self.play(group_2022.animate.set_opacity(0.5))
        
        title_2023 = Tex(r"\textbf{Hybrid QuaDRiGa/FDTD}", color=WHITE).scale(0.7).to_edge(LEFT).shift(RIGHT * 2)
        year_2023 = Tex(r"\textbf{2023}", color=WHITE).scale(0.7).to_edge(RIGHT)
        group_2023 = VGroup(title_2023, year_2023)
        group_2023.shift(DOWN * 1)

        new_arrow_end = LEFT * 6.5 + UP * (group_2023.get_bottom()[1] - 0.3)
        new_arrow = Arrow(start=arrow.get_start(), end=new_arrow_end, color=BLUE, stroke_width=15)
        
        self.play(Write(group_2023), Transform(arrow, new_arrow), run_time=1)
        self.wait(0.5)
        self.next_slide()

        # Reduce opacity and display new text
        self.play(group_2023.animate.set_opacity(0.5))
        
        title_2024 = Tex(r"\textbf{Hybrid RT-based QuaDRiGa/FDTD}", color=WHITE).scale(0.7).to_edge(LEFT).shift(RIGHT * 2)
        year_2024 = Tex(r"\textbf{2024}", color=WHITE).scale(0.7).to_edge(RIGHT)
        group_2024 = VGroup(title_2024, year_2024)
        group_2024.shift(DOWN * 3)

        new_arrow_end = LEFT * 6.5 + UP * (group_2024.get_bottom()[1] - 0.3)
        new_arrow = Arrow(start=arrow.get_start(), end=new_arrow_end, color=BLUE, stroke_width=15)
        
        self.play(Write(group_2024), Transform(arrow, new_arrow), run_time=1)
        self.wait(0.5)
        self.next_slide()
