from manim import *
import numpy as np
import math
import os

class TxBeamformingArcs(Scene): # Changed class name for clarity if needed, but keeping it for now
    def construct(self):
        self.camera.background_color =  WHITE
        # --- Configuration ---
        num_antennas = 8
        antenna_spacing = 0.5  # Spacing between antennas
        wave_speed = 2.5       # Speed at which wavefronts expand
        wave_frequency = 2.0   # Increased frequency
        max_radius = 6         # How far the waves expand before fading
        pulse_interval = 1.0 / wave_frequency # Time between emitting new wavefronts (now shorter)
        wave_color = BLUE
        wave_stroke_width = 2
        broadside_duration = 2 # Reduced duration
        steering_animation_duration = 15 # Even slower phase changes
        transition_duration = 1.0 # Duration for wave-to-pattern fade

        # --- Antenna Array Setup ---
        antenna_positions = [
            np.array([(i - (num_antennas - 1) / 2) * antenna_spacing, -3, 0])
            for i in range(num_antennas)
        ]
        antennas = VGroup(*[Dot(point=pos, radius=0.1, color=BLACK) for pos in antenna_positions])
        antenna_label = Text("Antenna Array", font_size=24, color=BLACK).next_to(antennas, DOWN, buff=0.5) # Reset position

        # Add Title
        title = Text("Beamsteering", font_size=48, color=BLACK).to_edge(UP)
        self.add(title)

        self.add(antennas, antenna_label) # Keep antenna array visible throughout

        # --- Phase Gradient Display & Visualization ---
        delta_phi_tracker = ValueTracker(0) # Tracks the phase gradient value (oscillates +/- PI/4)
        center_index = (num_antennas - 1) / 2

        # Text display: Δφ = value
        delta_phi_label = MathTex(r"\Delta\phi = ", font_size=36, color=BLACK)
        delta_phi_value = always_redraw(
            lambda: DecimalNumber(
                delta_phi_tracker.get_value(),
                num_decimal_places=2,
                show_ellipsis=False,
                include_sign=True, # Show + or -
                unit=r"\,\,\text{ rad}" # Add rad unit
                # Color will be set below
            ).set_color(BLACK).scale(0.8).next_to(delta_phi_label, RIGHT, buff=0.15) # Explicitly set color here
        )
        delta_phi_text_group = VGroup(delta_phi_label, delta_phi_value).to_corner(UR, buff=0.5)

        # Explanation Text (Corrected Arrow)
        explanation_text = MathTex(
            r"\text{Applying phase gradient } (\Delta\phi)",
            r"\text{ steers beam }",
            # Use LaTeX \rightarrow in math mode, colored yellow
            r"(\boldsymbol{\longrightarrow})", # Add parentheses, use bold longrightarrow
            font_size=30,
            color=BLACK # Set entire explanation text to black
        )
        explanation_text[2].set_color(GREEN) # Color the arrow part green
        explanation_text.next_to(delta_phi_text_group, DOWN, buff=0.5, aligned_edge=RIGHT)


        # Phase visualization circle
        phase_circle_radius = 0.5
        phase_circle = Circle(radius=phase_circle_radius, color=BLACK)
        # Corrected angle direction (removed negative sign)
        phase_indicator = always_redraw(lambda: Line(
                phase_circle.get_center(),
                phase_circle.point_at_angle(delta_phi_tracker.get_value()), # Use positive angle
                color=GREEN, stroke_width=3
            )
        )
        # Add markers/labels
        phase_markers = VGroup(
            # Markers for the +/- PI/4 oscillation range
            Dot(point=phase_circle.point_at_angle(0), color=BLACK).scale(0.5),
            Tex("0", font_size=18, color=BLACK).next_to(phase_circle.point_at_angle(0), RIGHT, buff=0.1),
            Dot(point=phase_circle.point_at_angle(PI/4), color=BLACK).scale(0.5),
            MathTex(r"\pi/4", font_size=18, color=BLACK).next_to(phase_circle.point_at_angle(PI/4), UR, buff=0.1),
            Dot(point=phase_circle.point_at_angle(-PI/4), color=BLACK).scale(0.5),
            MathTex(r"-\pi/4", font_size=18, color=BLACK).next_to(phase_circle.point_at_angle(-PI/4), DR, buff=0.1)
        )

        phase_vis_group = VGroup(phase_circle, phase_markers, phase_indicator) # Indicator on top
        phase_vis_group.next_to(explanation_text, DOWN, buff=0.3, aligned_edge=RIGHT)

        # --- Beam Indicator ---
        # Max steering angle assumed visually for PI/4 phase gradient
        max_steer_angle = PI / 6 # e.g., 30 degrees
        self.last_steer_angle = 0 # Initialize for workaround

        # --- Beam Indicator (Replaced with SVG) ---
        cigar_svg_path = "media/images/tx_beamforming_arcs/cigar_pattern.svg"
        if not os.path.exists(cigar_svg_path):
             logger.warning(f"SVG file not found at {cigar_svg_path}. Cannot create beam indicator.")
             beam_indicator = Circle(radius=0.1, color=RED, fill_opacity=1).set_opacity(0) # Placeholder
        else:
             beam_indicator = SVGMobject(cigar_svg_path)
             # Scale the SVG to a reasonable height (e.g., 3 units like the original arrow)
             beam_indicator.scale_to_fit_height(3)
             # Position the bottom center of the SVG at the antenna array center
             beam_indicator.move_to(antennas.get_center(), aligned_edge=DOWN)
             #beam_indicator.set_opacity(0) # Start invisible for FadeIn

        def update_beam_indicator(svg_mob):
            # Workaround: Rotate incrementally instead of using become
            current_delta_phi = delta_phi_tracker.get_value()
            limited_delta_phi = np.clip(current_delta_phi, -PI/4, PI/4)
            current_steer_angle = -(limited_delta_phi / (PI/4)) * max_steer_angle

            # Calculate the change in angle needed from the last frame
            delta_angle = current_steer_angle - self.last_steer_angle

            # Apply only the delta rotation
            svg_mob.rotate(delta_angle, about_point=antennas.get_center())

            # Update the last angle
            self.last_steer_angle = current_steer_angle
        # Updater will be added after FadeIn

        # --- Continuous Wavefront Simulation ---
        all_wavefronts = VGroup() # Holds all currently active arcs
        scene_time = 0.0          # Keep track of scene time for emission
        last_emission_time = -pulse_interval # Ensure emission on first frame

        def generate_wave_set(current_delta_phi, emission_time):
            """Generates a set of 8 arcs for a single emission time."""
            wave_set = VGroup()
            for i, ant_pos in enumerate(antenna_positions):
                phase_rad = (i - center_index) * current_delta_phi
                time_delay = phase_rad / (2 * PI * wave_frequency) if wave_frequency != 0 else 0

                # Revert back to Arc for upper semi-circle
                # Explicitly set stroke_color and fill_opacity
                arc = Arc(
                    radius=0.01, start_angle=PI, angle=-PI, # Top semi-circle
                    arc_center=ant_pos, # Set initial center correctly
                    stroke_color=wave_color, # Explicitly set stroke color
                    stroke_width=wave_stroke_width,
                    fill_opacity=0 # Explicitly set no fill
                )
                arc.emission_time = emission_time
                arc.time_delay = time_delay
                arc.original_center = ant_pos # Store original center explicitly
                arc.is_visible = True # Add a flag to track visibility state
                wave_set.add(arc)
            return wave_set

        def update_waves(mobj, dt):
            """Updater function for managing wavefronts."""
            nonlocal scene_time, last_emission_time
            scene_time += dt

            if scene_time >= last_emission_time + pulse_interval:
                last_emission_time += pulse_interval
                # Use the *current* tracker value when emitting
                new_waves = generate_wave_set(delta_phi_tracker.get_value(), last_emission_time)
                mobj.add(new_waves)

            # --- Individual Arc Update Logic (Revised) ---
            # Iterate through copies to avoid modification issues during iteration
            for wave_set in list(mobj.submobjects):
                # Check if the wave_set itself is still valid (might be removed in rare cases)
                if wave_set not in mobj:
                    continue

                set_should_be_removed = True # Assume removable until proven otherwise
                for arc in wave_set:
                    # Skip if arc is already marked invisible
                    if not getattr(arc, 'is_visible', True):
                        # Ensure opacity is 0 if marked invisible
                        if arc.get_stroke_opacity() > 0:
                           arc.set_stroke(opacity=0)
                        continue # Move to next arc in the set

                    # Calculate arc properties
                    time_since_emission = scene_time - arc.emission_time
                    effective_time = time_since_emission - arc.time_delay

                    if effective_time >= 0:
                        current_radius = effective_time * wave_speed
                        opacity = max(0, 1 - (current_radius / max_radius)**2)

                        if current_radius >= max_radius or opacity <= 1e-6: # Use a small threshold for opacity check
                            arc.set_stroke(opacity=0)
                            arc.is_visible = False # Mark as invisible
                        else:
                            # Update the arc's properties
                            arc.become(Arc(
                                radius=max(0.01, current_radius),
                                start_angle=PI, angle=-PI,
                                arc_center=arc.original_center,
                                stroke_color=wave_color,
                                stroke_width=wave_stroke_width,
                                fill_opacity=0
                            )).set_stroke(opacity=opacity)
                            set_should_be_removed = False # This set is still active
                    else:
                        # Arc hasn't effectively started yet
                        arc.set_stroke(opacity=0)
                        set_should_be_removed = False # This set is still active

                # If all arcs in the set are now marked as invisible, remove the whole set
                if set_should_be_removed:
                    mobj.remove(wave_set)

        all_wavefronts.add_updater(update_waves)
        self.add(all_wavefronts)

        # --- Inter-element Phase Viz ---
        # Find first two antennas
        idx1 = 0
        idx2 = 1
        ant1_pos = antennas[idx1].get_center()
        ant2_pos = antennas[idx2].get_center()

        # Create arrow and label for inter-element phase
        # Use MathTex for the arrow as well for consistency
        inter_element_arrow = MathTex(r"\leftrightarrow", color=GREEN).scale(1.5)
        inter_element_arrow.move_to(midpoint(ant1_pos, ant2_pos) + DOWN*0.3)
        inter_element_label = MathTex(r"\Delta\phi", font_size=24, color=GREEN).next_to(inter_element_arrow, DOWN, buff=0.15)
        inter_element_group = VGroup(inter_element_arrow, inter_element_label)

        # Show inter-element viz
        # self.play(FadeOut(title, shift=UP*0.5), run_time=0.5) # Keep title visible
        self.play(Create(inter_element_group), run_time=1)
        self.wait(1) # Shorter wait
        # self.play(FadeOut(inter_element_group, shift=DOWN*0.2), run_time=0.5) # Keep inter-element viz visible
        self.wait(0.2) # Shorter wait

        # --- Initial Broadside Visualization ---
        self.wait(broadside_duration) # Show broadside pulsing

        # --- Animate Phase Steering ---
        self.play(
            FadeIn(delta_phi_text_group),
            FadeIn(explanation_text),
            FadeIn(beam_indicator), # Fade in beam indicator (now defined)
            FadeIn(phase_vis_group)
        )
        self.wait(0.2) # Reduced wait
        beam_indicator.add_updater(update_beam_indicator) # Add beam updater AFTER FadeIn

        # --- Antenna Pattern Setup (Removed - Integrated into beam_indicator) ---
        # Animate delta_phi bouncing between -PI/4 and PI/4
        # Calculate segment durations
        num_bounces = 3 # Adjust bounces for new duration
        # Allocate total steering duration for bounces
        time_to_pi_4 = steering_animation_duration / (1 + 2 * num_bounces) # Time for initial 0 -> pi/4 move
        time_per_bounce = (steering_animation_duration - time_to_pi_4) / num_bounces # Time for a full +/-pi/4 bounce
        # Transition roughly halfway through the total steering animation time
        transition_time_target = steering_animation_duration / 2
        transition_duration = 1.0 # Duration for the fade transition (can adjust)
        has_transitioned = False # Flag to ensure transition happens only once

        # Initial move
        self.play(
            delta_phi_tracker.animate.set_value(PI/4),
            run_time=time_to_pi_4,
            rate_func=linear
        )

        # Bouncing loop
        current_anim_time = time_to_pi_4 # Time elapsed in steering phase after initial move

        for i in range(num_bounces):
            # Animate to -PI/4
            run_time_segment = time_per_bounce / 2
            # Check if transition should happen during this segment
            if not has_transitioned and current_anim_time < transition_time_target <= current_anim_time + run_time_segment:
                # Split the animation
                time_before_trans = transition_time_target - current_anim_time
                time_after_trans = run_time_segment - time_before_trans
                target_val_at_trans = delta_phi_tracker.get_value() + ((-PI/4 - delta_phi_tracker.get_value()) * (time_before_trans / run_time_segment))

                self.play(delta_phi_tracker.animate.set_value(target_val_at_trans), run_time=time_before_trans, rate_func=rate_functions.smooth)
                # --- Perform Transition (Fade out waves only) ---
                all_wavefronts.clear_updaters() # Stop updating waves
                self.play(
                    FadeOut(all_wavefronts, shift=DOWN*0.1),
                    run_time=transition_duration
                 )
                self.remove(all_wavefronts) # Remove waves from scene after fade
                # beam_indicator (SVG) is already visible and updating
                has_transitioned = True
                # --- Continue animation ---
                self.play(delta_phi_tracker.animate.set_value(-PI/4), run_time=time_after_trans, rate_func=rate_functions.smooth)

            else: # No transition in this segment
                 self.play(
                    delta_phi_tracker.animate.set_value(-PI/4),
                    run_time=run_time_segment,
                    rate_func=rate_functions.smooth
                 )
            current_anim_time += run_time_segment

            # Animate to PI/4
            run_time_segment = time_per_bounce / 2
            # Check if transition should happen during this segment
            if not has_transitioned and current_anim_time < transition_time_target <= current_anim_time + run_time_segment:
                 # Split the animation
                time_before_trans = transition_time_target - current_anim_time
                time_after_trans = run_time_segment - time_before_trans
                target_val_at_trans = delta_phi_tracker.get_value() + ((PI/4 - delta_phi_tracker.get_value()) * (time_before_trans / run_time_segment))

                self.play(delta_phi_tracker.animate.set_value(target_val_at_trans), run_time=time_before_trans, rate_func=rate_functions.smooth)
                 # --- Perform Transition (Fade out waves only) ---
                all_wavefronts.clear_updaters() # Stop updating waves
                self.play(
                    FadeOut(all_wavefronts, shift=DOWN*0.1),
                    run_time=transition_duration
                 )
                self.remove(all_wavefronts) # Remove waves from scene after fade
                # beam_indicator (SVG) is already visible and updating
                has_transitioned = True
                 # --- Continue animation ---
                self.play(delta_phi_tracker.animate.set_value(PI/4), run_time=time_after_trans, rate_func=rate_functions.smooth)

            else: # No transition in this segment
                 self.play(
                    delta_phi_tracker.animate.set_value(PI/4),
                    run_time=run_time_segment,
                    rate_func=rate_functions.smooth
                 )
            current_anim_time += run_time_segment

        # Ensure wave fade-out happens if target time was somehow missed exactly
        if not has_transitioned:
             all_wavefronts.clear_updaters()
             self.play(
                FadeOut(all_wavefronts, shift=DOWN*0.1),
                run_time=transition_duration
             )
             self.remove(all_wavefronts)
             # beam_indicator (SVG) is already visible and updating
        # Optional: Animate back to 0 if needed for a final state
        # self.play(delta_phi_tracker.animate.set_value(0), run_time=steering_animation_duration / 3)

        # Keep the final state visible briefly
        self.wait(0.5)

        # Cleanup updater
        all_wavefronts.remove_updater(update_waves)
        beam_indicator.remove_updater(update_beam_indicator)
        # antenna_pattern updater removed as it's now part of beam_indicator