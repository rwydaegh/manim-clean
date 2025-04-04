from manim import *
from manim_slides import Slide

class AntennaBeamforming(Slide):
    def construct(self):
        # Step 3: Draw Antenna Array
        num_antennas = 8
        antenna_radius = 0.1
        antenna_positions = [np.array([i - num_antennas / 2, 0, 0]) for i in range(num_antennas)]
        antennas = VGroup(*[Dot(point=pos, radius=antenna_radius, color=BLUE) for pos in antenna_positions])
        self.play(Create(antennas))
        self.next_slide()
        
        # Step 4: Simulate Signal Transmission
        wave_lines = VGroup()
        for pos in antenna_positions:
            wave = always_redraw(lambda: Circle(radius=0.5 + self.renderer.time % 1, color=YELLOW).move_to(pos))
            wave_lines.add(wave)
        self.play(Create(wave_lines), run_time=2)
        self.next_slide()

        # Step 5: Illustrate Phase Shifting
        phase_shifts = [Line(pos, pos + UP*0.5, color=RED) for pos in antenna_positions]
        self.play(*[Create(phase) for phase in phase_shifts])
        self.next_slide()

        # Step 6: Demonstrate Constructive Interference
        # Illustrate the focused beam
        beam_direction = np.array([2, 1, 0])
        beam = Arrow(start=ORIGIN, end=2 * beam_direction, buff=0, color=GREEN)
        self.play(GrowArrow(beam))
        self.next_slide()

        # Step 7: Add Labels and Explanations
        labels = VGroup(
            Text("Antennas").next_to(antennas, UP),
            Text("Signals").next_to(wave_lines, DOWN),
            Text("Phase Shifts").next_to(phase_shifts[0], RIGHT),
            Text("Beamforming").next_to(beam, RIGHT)
        )
        self.play(Write(labels))
        self.next_slide()

        # Step 8: Animate the Beamforming
        for i in range(3):
            self.play(beam.animate.shift(UP * 0.5), run_time=1)
            self.play(beam.animate.shift(DOWN * 0.5), run_time=1)
        self.next_slide()

        self.wait(2)

