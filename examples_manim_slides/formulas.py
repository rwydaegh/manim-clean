from manim import *
from manim_slides import Slide
import matplotlib.pyplot as plt

class Formulas(Slide):
    def construct(self):
        # Write vector electric field
        e_field = MathTex(r"\vec{E}(\vec{r}, t)")
        e_field.scale(2)

        # Write the electric field vector
        self.play(Write(e_field), run_time=2)
        
        self.wait(0.5)
        self.next_slide()

        # Define the norm of the electric field
        e_avg_field = MathTex(r"\langle", r"\vec{E}(\vec{r}, t)",  r"\rangle_t")
        e_avg_field.set_color_by_tex(r"\langle", RED)
        e_avg_field.set_color_by_tex(r"\rangle_t", RED)
        e_avg_field.scale(2)

        # Define the averaging formula
        averaging_explain = MathTex(r"\langle \cdot \rangle_t = \frac{1}{T} \int_{0}^{T} \cdot \, \mathrm{d}t", substrings_to_isolate=[r"\langle", r"\rangle_t"])
        averaging_explain.set_color_by_tex(r"\langle", RED)
        averaging_explain.set_color_by_tex(r"\rangle_t", RED)
        averaging_explain.shift(2*DOWN)

        # Transform e_field to e_norm_field
        self.play(TransformMatchingTex(e_field, e_avg_field), Write(averaging_explain), run_time=1)
        
        self.wait(0.5)
        self.next_slide()

        # Define the time-averaged norm of the electric field
        e_norm = MathTex(r"\|", r"\langle", r"\vec{E}(\vec{r}, t)", r"\rangle_t", r"\|")
        e_norm.set_color_by_tex(r"\|", GREEN)
        e_norm.set_color_by_tex(r"\langle", RED)
        e_norm.set_color_by_tex(r"\rangle_t", RED)
        e_norm.scale(2)

        # Transform e_norm_field to e_norm
        self.play(TransformMatchingTex(e_avg_field, e_norm), run_time=1)
        
        self.wait(0.5)
        self.next_slide()

        # Write propagation-wise averaging above it
        prop_avg = Tex(r"\textit{Propagation-wise} averaging")
        prop_avg.scale(2)
        prop_avg.shift(2*UP)

        self.play(Write(prop_avg), run_time=2)
        self.wait(0.5)

        # Fade out the averaging explanation and propagation-wise averaging text
        self.play(FadeOut(averaging_explain), FadeOut(prop_avg))
        self.play(e_norm.animate.shift(3*UP), run_time=1)

        self.wait(0.5)
        self.next_slide()

        e_prop_to_cos = MathTex(r"{{\vec{E}(\vec{r})}} \propto \cos(\|{{\vec{r}}}\|)")
        e_prop_to_cos.shift(UP)

        h_prop_to_sin = MathTex(r"{{\vec{H}(\vec{r})}} \propto \sin(\|{{\vec{r}}}\|)")
        h_prop_to_sin.shift(DOWN)

        self.play(Write(e_prop_to_cos), run_time = 2)

        self.wait(0.5)
        self.next_slide()

        self.play(Write(h_prop_to_sin), run_time = 2)

        self.wait(0.5)
        self.next_slide()

        # Fade both out
        h_avg_norm = MathTex(r"\|", r"\langle", r"\vec{H}(\vec{r}, t)", r"\rangle_t", r"\|")
        h_avg_norm.set_color_by_tex(r"\|", GREEN)
        h_avg_norm.set_color_by_tex(r"\langle", RED)
        h_avg_norm.set_color_by_tex(r"\rangle_t", RED)
        h_avg_norm.scale(2)
        h_avg_norm.shift(3*UP)
        self.play(FadeOut(e_prop_to_cos), FadeOut(h_prop_to_sin), ReplacementTransform(e_norm, h_avg_norm), run_time=1)

        self.wait(0.5)
        self.next_slide()

        '''
        S_def = MathTex(r"{{\vec{S}}} = {{\vec{E}}} \times {{\vec{H}}")
        S_def.scale(2)

        self.play(Write(S_def), FadeOut(h_norm_avg), run_time = 2)

        self.wait(0.5)
        self.next_slide()
        '''

        Sinc_def = MathTex(
            r"S_\mathrm{inc}", r"=", r"\langle", r"\|", r"\vec{S}", r"\|", r"\rangle_t", r"=", 
            r"\langle", r"\|", r"\vec{E}", r"\times", r"\vec{H}", r"^*", r"\|", r"\rangle_t"
        )
        Sinc_def.set_color_by_tex(r"\|", GREEN)
        Sinc_def.set_color_by_tex(r"\langle", RED)
        Sinc_def.set_color_by_tex(r"\rangle_t", RED)
        Sinc_def.scale(2)

        self.play(Write(Sinc_def), FadeOut(h_avg_norm), run_time = 2)

        self.wait(0.5)
        self.next_slide()

        # Write exposure-wise averaging above it
        exp_avg = Tex(r"\textit{Exposure-wise} averaging")
        exp_avg.scale(2)
        exp_avg.shift(2*UP)

        self.play(Write(exp_avg), run_time=2)

        self.wait(0.5)
        self.next_slide()

        # Fade out the exposure-wise averaging text and place the |E x H| at the top
        Sinc_top = MathTex(
            r"\langle", r"\|", r"\vec{E}", r"\times", r"\vec{H}", r"^*", r"\|", r"\rangle_t"
        )
        Sinc_top.set_color_by_tex(r"\|", GREEN)
        Sinc_top.set_color_by_tex(r"\langle", RED)
        Sinc_top.set_color_by_tex(r"\rangle_t", RED)
        Sinc_top.scale(2)
        Sinc_top.shift(3*UP)

        self.play(FadeOut(exp_avg), ReplacementTransform(Sinc_def, Sinc_top), run_time=1)

        self.wait(0.5)
        self.next_slide()


