from manim import *
import numpy as np
import math
import matplotlib.pyplot as plt
import io
from PIL import Image
from manim import ImageMobject # Correct import path

class RxBeamformingPhasors(Scene):
    def construct(self):
        # --- Configuration ---
        num_mpc = 3
        wave_speed = 2.5
        wave_frequency = 1.0
        wave_amplitude = 1.0
        max_radius_time_domain = 12
        pulse_interval = 1.0 / wave_frequency
        k = 2 * PI * wave_frequency / wave_speed

        box_width = 6
        box_height = 4
        box_color = BLACK # Changed for white background
        rx_color = RED
        phasor_colors = [BLUE, GREEN, ORANGE] # Adjusted colors slightly
        heatmap_colormap = "viridis"

        # Animation timings
        time_domain_duration_per_mpc = 4
        transition_duration = 0.5
        initial_sum_hold_duration = 1.5
        morph_align_duration = 5
        final_hold_duration = 3

        # --- Scene Elements ---
        self.camera.background_color = WHITE # Set background color
        box = Rectangle(
            width=box_width, height=box_height, color=box_color, stroke_width=2
        ).shift(ORIGIN)
        rx_position = box.get_center()
        rx_dot = Dot(point=rx_position, color=rx_color, radius=0.1)
        rx_label = Text("Rx", font_size=20, color=BLACK).next_to(rx_dot, UP, buff=0.15) # Label above, black
        title = Text("Hotspots", font_size=48, color=BLACK).to_edge(UP) # Black title
        self.add(title, box, rx_dot, rx_label)

        # --- MPC Setup ---
        mpc_aoa = np.array([ PI * 3/4, PI * 1/4, PI * 5/4 ]) # TL, TR, BL
        source_distance = 8
        mpc_source_positions = np.array([
            rx_position + source_distance * np.array([np.cos(angle), np.sin(angle), 0])
            for angle in mpc_aoa
        ])
        mpc_initial_phases = np.array([PI/3, PI * 8/10, PI * 3/2])
        mpc_time_delays = mpc_initial_phases / (2 * PI * wave_frequency)
        # Step 1 Complete

        # --- Helper Functions ---
        def generate_wave_set_rx(source_pos, emission_time, initial_delay, color):
             arc = Arc(
                 radius=0.01, start_angle=0, angle=TAU,
                 arc_center=source_pos, stroke_color=color, stroke_width=3, fill_opacity=0
             )
             arc.emission_time = emission_time
             arc.time_delay = initial_delay
             arc.original_center = source_pos
             arc.arc_color = color
             return arc

        def update_wave_group(mobj, dt, source_pos, delay, color, time_tracker):
            time_tracker['scene_time'] += dt
            scene_time_local = time_tracker['scene_time']
            last_emission_time_local = time_tracker['last_emission']
            new_waves_this_frame = VGroup()
            if scene_time_local >= last_emission_time_local + pulse_interval:
                time_tracker['last_emission'] += pulse_interval
                last_emission_time_local = time_tracker['last_emission']
                new_wave = generate_wave_set_rx(source_pos, scene_time_local, delay, color)
                new_wave.emission_time = scene_time_local
                new_waves_this_frame.add(new_wave)
            mobj.add(*new_waves_this_frame)
            arcs_to_remove = []
            for arc in mobj:
                time_since_emission = scene_time_local - arc.emission_time
                effective_time = time_since_emission - arc.time_delay
                if effective_time >= 0:
                    current_radius = effective_time * wave_speed
                    if current_radius > max_radius_time_domain:
                         if arc not in arcs_to_remove: arcs_to_remove.append(arc)
                         continue
                    vec_to_rx = rx_position - arc.original_center
                    center_angle = np.arctan2(vec_to_rx[1], vec_to_rx[0])
                    angle_span = PI * 1.5
                    start_angle = center_angle - angle_span / 2
                    arc_color = getattr(arc, 'arc_color', color)
                    new_arc_points = Arc(
                        radius=max(0.01, current_radius), start_angle=start_angle, angle=angle_span,
                        arc_center=arc.original_center,
                    ).points
                    arc.set_points(new_arc_points)
                    arc.set_stroke(color=arc_color, width=3, opacity=max(0, 1 - (current_radius / max_radius_time_domain)**2))
                    arc.set_fill(opacity=0)
                else: arc.set_opacity(0)
            mobj.remove(*arcs_to_remove)

        # Define grid for heatmap calculation
        resolution = 100
        x_coords = np.linspace(box.get_left()[0], box.get_right()[0], resolution)
        y_coords = np.linspace(box.get_bottom()[1], box.get_top()[1], resolution)
        xx, yy = np.meshgrid(x_coords, y_coords)
        grid_points = np.stack([xx.ravel(), yy.ravel(), np.zeros(resolution*resolution)], axis=-1)

        # Helper to calculate single MPC field REAL PART
        def calculate_single_mpc_real_part(points, source_pos, k_val, initial_phase, amplitude):
            displacements = points - source_pos
            distances = np.linalg.norm(displacements, axis=1)
            phases = k_val * distances + initial_phase
            return amplitude * np.cos(phases)

        # Helper to generate buffer for a single MPC heatmap (using real part)
        def generate_single_heatmap_buffer(mpc_idx):
            real_part_values = calculate_single_mpc_real_part(
                grid_points, mpc_source_positions[mpc_idx], k, mpc_initial_phases[mpc_idx], wave_amplitude
            )
            heatmap_data = real_part_values.reshape((resolution, resolution))
            vmin = -wave_amplitude
            vmax = wave_amplitude
            fig, ax = plt.subplots(figsize=(box_width/2, box_height/2))
            im = ax.imshow(
                heatmap_data, cmap=heatmap_colormap, origin='lower',
                extent=[box.get_left()[0], box.get_right()[0], box.get_bottom()[1], box.get_top()[1]],
                vmin=vmin, vmax=vmax
            )
            ax.axis('off')
            fig.tight_layout(pad=0)
            buf = io.BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0, transparent=True)
            buf.seek(0)
            plt.close(fig)
            return buf

        # --- Step 2: Time Domain + Individual Static Heatmaps ---
        print("--- Starting Step 2: Time Domain + Static Heatmaps ---")
        time_trackers = {}
        label_corners = [UL, UR, DL] # Define corners for labels
        for mpc_index in range(num_mpc):
            current_mpc_waves = VGroup()
            current_source_pos = mpc_source_positions[mpc_index]
            current_delay = mpc_time_delays[mpc_index]
            current_color = phasor_colors[mpc_index]

            static_heatmap_buf = generate_single_heatmap_buffer(mpc_index)
            static_heatmap_image = ImageMobject(Image.open(static_heatmap_buf))
            static_heatmap_image.set_height(box_height).move_to(box.get_center()).set_opacity(0.7)

            aoa = mpc_aoa[mpc_index]
            arrow_start_point = rx_position + box_width/2 * np.array([np.cos(aoa + PI), np.sin(aoa + PI), 0])
            edge_point = box.get_boundary_point(arrow_start_point - rx_position)
            arrow = Arrow(
                start=edge_point, end=rx_position, buff=0.2, color=current_color,
                stroke_width=4, max_tip_length_to_length_ratio=0.15, max_stroke_width_to_length_ratio=3
            )

            # Position Label in appropriate corner
            corner = label_corners[mpc_index]
            mpc_label = Text(f"MPC {mpc_index+1}", font_size=24, color=BLACK).to_corner(corner) # Black label

            time_trackers[mpc_index] = {'scene_time': 0.0, 'last_emission': -pulse_interval}
            updater_lambda = lambda m, dt, _src=current_source_pos, _del=current_delay, \
                                    _col=current_color, _trk=time_trackers[mpc_index]: \
                                update_wave_group(m, dt, _src, _del, _col, _trk)
            current_mpc_waves.add_updater(updater_lambda)

            self.add(current_mpc_waves)
            self.play(
                FadeIn(mpc_label), FadeIn(arrow), FadeIn(static_heatmap_image),
                run_time=0.5
            )
            self.wait(time_domain_duration_per_mpc)

            current_mpc_waves.remove_updater(updater_lambda)
            self.play(
                FadeOut(mpc_label), FadeOut(arrow), FadeOut(static_heatmap_image),
                FadeOut(current_mpc_waves), run_time=0.5
            )
        print("--- Finished Step 2 ---")
        # Step 2 Complete

        # --- Step 3: Transition ---
        self.wait(transition_duration)
        # Step 3 Complete

        # --- Step 4: Initial Summed Heatmap & Phasors ---
        print("--- Starting Step 4: Initial Summed State ---")
        target_phase = 0.0
        rotation_angles = []
        phasor_vectors_np = []
        current_phases_at_rx = []
        for i in range(num_mpc):
            source_pos = mpc_source_positions[i]
            initial_phase = mpc_initial_phases[i]
            dist_to_rx = np.linalg.norm(rx_position - source_pos)
            phase_at_rx = (k * dist_to_rx + initial_phase)
            current_phase = phase_at_rx % (2 * PI)
            current_phases_at_rx.append(current_phase)
            rotation_angle = target_phase - current_phase
            rotation_angles.append(rotation_angle)
            phasor_np = wave_amplitude * np.array([np.cos(current_phase), np.sin(current_phase), 0])
            phasor_vectors_np.append(phasor_np)

        def calculate_summed_field_intensity(points, alignment_value):
            total_complex_field = np.zeros(points.shape[0], dtype=complex)
            for i in range(num_mpc):
                source_pos = mpc_source_positions[i]
                initial_phase = mpc_initial_phases[i]
                rot_angle = rotation_angles[i]
                displacements = points - source_pos
                distances = np.linalg.norm(displacements, axis=1)
                phi_initial = k * distances + initial_phase
                phi_adjusted = phi_initial + alignment_value * rot_angle
                total_complex_field += wave_amplitude * np.exp(1j * phi_adjusted)
            return np.abs(total_complex_field)**2

        def generate_summed_heatmap_buffer(alignment_val):
            field_intensity = calculate_summed_field_intensity(grid_points, alignment_val)
            heatmap_data = field_intensity.reshape((resolution, resolution))
            vmin = np.percentile(heatmap_data, 1)
            vmax = np.percentile(heatmap_data, 99.5)
            fig, ax = plt.subplots(figsize=(box_width/2, box_height/2))
            im = ax.imshow(
                heatmap_data, cmap=heatmap_colormap, origin='lower',
                extent=[box.get_left()[0], box.get_right()[0], box.get_bottom()[1], box.get_top()[1]],
                vmin=vmin, vmax=vmax, interpolation='bicubic'
            )
            ax.axis('off')
            fig.tight_layout(pad=0)
            buf = io.BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0, transparent=True)
            buf.seek(0)
            plt.close(fig)
            return buf

        initial_summed_buf = generate_summed_heatmap_buffer(0.0)
        summed_heatmap_image = ImageMobject(Image.open(initial_summed_buf))
        summed_heatmap_image.set_height(box_height).move_to(box.get_center()).set_opacity(0.8)

        phasors_initial = VGroup()
        for i in range(num_mpc):
             phasor_vec = Vector(
                 phasor_vectors_np[i], color=phasor_colors[i], stroke_width=4
             ).shift(rx_position)
             phasors_initial.add(phasor_vec)

        initial_state_label = Text("Initial State", font_size=24, color=BLACK).next_to(box, DOWN, buff=0.3) # Black label
        initial_state_label.set_z_index(20)

        self.play(
            FadeIn(summed_heatmap_image), Create(phasors_initial), Write(initial_state_label),
            run_time=1
        )
        self.wait(initial_sum_hold_duration)
        print("--- Finished Step 4 ---")
        # Step 4 Complete

        # --- Step 5: Morph Heatmap & Align Phasors/Dials ---
        print("--- Starting Step 5: Morph and Align ---")
        self.play(FadeOut(initial_state_label), run_time=0.2)

        dials = VGroup()
        dial_indicators = VGroup()
        dial_radius = 0.4 # Increased radius
        dial_label_offset = 1.0 # Offset for dials relative to label corners

        # Position dials relative to the corners using to_corner().shift()
        dial_positions = []
        # label_corners defined earlier
        for i in range(num_mpc):
            corner = label_corners[i]
            if np.array_equal(corner, UL) or np.array_equal(corner, UR):
                offset_dir = DOWN
            else: # DL corner
                offset_dir = UP
            # Create a temporary point at the corner and shift it
            dial_pos = Dot().to_corner(corner).shift(offset_dir * dial_label_offset).get_center()
            dial_positions.append(dial_pos)

        # Also create the MPC labels again for this phase, positioned near dials
        mpc_labels_step5 = VGroup()
        label_offset_factor = 0.0 # Smaller offset for labels vs dials
        for i in range(num_mpc):
            dial_center = dial_positions[i]
            dial_circle = Circle(radius=dial_radius, color=phasor_colors[i], stroke_width=2).move_to(dial_center)
            indicator_line = Line(
                start=dial_center, end=dial_center + dial_radius * RIGHT,
                color=phasor_colors[i], stroke_width=3
            ).rotate(current_phases_at_rx[i], about_point=dial_center)
            dials.add(dial_circle)
            dial_indicators.add(indicator_line)

            # Position label near the dial using similar logic
            corner = label_corners[i]
            if np.array_equal(corner, UL) or np.array_equal(corner, UR): offset_dir = DOWN
            else: offset_dir = RIGHT
            label_pos = Dot().to_corner(corner).shift(offset_dir * label_offset_factor).get_center()
            label = Text(f"MPC {i+1}", font_size=24, color=BLACK).move_to(label_pos) # Black label
            mpc_labels_step5.add(label)
        dials.set_z_index(20)
        dial_indicators.set_z_index(20)
        mpc_labels_step5.set_z_index(20) # Ensure labels are also on top

        alignment_tracker = ValueTracker(0.0)
        # Use become for heatmap morph
        def heatmap_updater(img_mob):
            alignment_val = alignment_tracker.get_value()
            new_buf = generate_summed_heatmap_buffer(alignment_val)
            new_img = ImageMobject(Image.open(new_buf))
            new_img.set_height(box_height).move_to(box.get_center()).set_opacity(0.8)
            img_mob.become(new_img)

        summed_heatmap_image.add_updater(heatmap_updater)

        phasor_rotations = [
            Rotate(phasors_initial[i], angle=rotation_angles[i], about_point=rx_position)
            for i in range(num_mpc)
        ]
        dial_rotations = [
            Rotate(dial_indicators[i], angle=rotation_angles[i], about_point=dial_positions[i])
            for i in range(num_mpc)
        ]

        aligning_label = Text("Aligning Phases...", font_size=24, color=BLACK).next_to(box, DOWN, buff=0.3) # Black label
        aligning_label.set_z_index(20)

        self.play(FadeIn(dials), FadeIn(dial_indicators), FadeIn(mpc_labels_step5), Write(aligning_label), run_time=0.5)
        self.play(
            alignment_tracker.animate.set_value(1.0),
            AnimationGroup(*phasor_rotations, lag_ratio=0),
            AnimationGroup(*dial_rotations, lag_ratio=0),
            run_time=morph_align_duration,
            rate_func=linear
        )
        summed_heatmap_image.remove_updater(heatmap_updater)
        self.play(FadeOut(aligning_label), run_time=0.2)
        print("--- Finished Step 5 ---")
        # Step 5 Complete

        # --- Step 6: Final Emphasis ---
        print("--- Starting Step 6: Final Emphasis ---")
        aligned_sum_label = Text("Aligned Sum (Hotspot)", font_size=24, color=BLACK).next_to(box, DOWN, buff=0.3) # Black label
        aligned_sum_label.set_z_index(20)
        phasors_initial.set_z_index(15)

        hotspot_animation = Flash(
            rx_dot, color=YELLOW, flash_radius=rx_dot.radius + 0.5,
            line_length=0.4, num_lines=16, run_time=1.5, time_width=0.5
        )
        # Keep MPC labels visible during flash
        self.play(Write(aligned_sum_label), FadeOut(dials), FadeOut(dial_indicators), run_time=0.5)
        self.play(hotspot_animation)
        print("--- Finished Step 6 ---")
        # Step 6 Complete

        # --- Step 7: Hold ---
        self.wait(final_hold_duration)
        # Step 7 Complete
        print("--- End of Construct ---")
