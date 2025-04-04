from manim import *
import numpy as np
import math

# --- Helper Functions (remain the same) ---
def on_segment(p, q, r):
    return (q[0] <= max(p[0], r[0]) and q[0] >= min(p[0], r[0]) and
            q[1] <= max(p[1], r[1]) and q[1] >= min(p[1], r[1]))
def orientation(p, q, r):
    val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
    if abs(val) < 1e-7: return 0
    return 1 if val > 0 else 2
def segments_intersect(p1, q1, p2, q2):
    o1 = orientation(p1, q1, p2); o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1); o4 = orientation(p2, q2, q1)
    if o1 != o2 and o3 != o4: return True
    if o1 == 0 and on_segment(p1, p2, q1): return True
    if o2 == 0 and on_segment(p1, q2, q1): return True
    if o3 == 0 and on_segment(p2, p1, q2): return True
    if o4 == 0 and on_segment(p2, q1, q2): return True
    return False
def line_intersection(p1, q1, p2, q2):
    xdiff = (p1[0] - q1[0], p2[0] - q2[0]); ydiff = (p1[1] - q1[1], p2[1] - q2[1])
    def det(a, b): return a[0] * b[1] - a[1] * b[0]
    div = det(xdiff, ydiff)
    if abs(div) < 1e-7: return None
    d = (det(p1, q1), det(p2, q2))
    x = det(d, xdiff) / div; y = det(d, ydiff) / div
    return np.array([x, y, 0])
def get_segment_intersection(p1, q1, p2, q2):
    if not segments_intersect(p1, q1, p2, q2): return None
    return line_intersection(p1, q1, p2, q2)

# --- Main Scene ---
class ReflectionAnimation(Scene):
    def construct(self):
        # Set background color for this scene
        self.camera.background_color = WHITE
        # --- Configuration ---
        wave_speed = 3.0
        wave_frequency = 0.75
        pulse_interval = 1.0 / wave_frequency
        max_radius_reflected = 5
        incident_wave_color = BLUE
        reflected_wave_color = RED
        normal_color = GREEN
        ray_color_incident = RED_D
        ray_color_reflected = RED_D
        current_density_color = RED
        wave_stroke_width = 2
        stage1_duration = 7
        stage2_duration = 2
        stage3_duration = 4
        stage4_duration = 1 # Fade out principle
        stage5_duration = 3 # Show current densities
        reflection_debounce_distance = 0.07
        plane_wave_length = config.frame_height + 2
        ray_length = 2.5

        # --- Scene Elements ---
        title = Text("Reflection", font_size=40, color=BLACK).to_edge(UP)

        wall_angle = np.arctan(-6/2)
        original_length = np.sqrt(2**2 + (-6)**2)
        new_length = original_length * 0.9
        wall_center = ORIGIN
        wall_half_vector = (new_length / 2) * normalize(np.array([2, -6, 0]))
        wall_start_new = wall_center - wall_half_vector
        wall_end_new = wall_center + wall_half_vector

        wall = Line(start=wall_start_new, end=wall_end_new, color=BLACK, stroke_width=3)
        wall_start = wall.get_start()
        wall_end = wall.get_end()
        wall_label = Text("Wall", font_size=30, color=BLACK).next_to(wall.get_center(), UR, buff=0.2)
        self.add(title, wall, wall_label)

        # --- Wave Simulation ---
        all_waves = VGroup()
        self.add(all_waves)

        # Store reflection events (time, point) for debouncing and later use
        reflection_events = []

        scene_time = 0.0
        last_emission_time = -pulse_interval
        plane_wave_start_x = -config.frame_width / 2 - 1

        best_reflection_info = { "point": None, "min_dist_sq": float('inf') }

        # --- Updater Function ---
        def update_reflection_waves(mobj, dt):
            nonlocal scene_time, last_emission_time, best_reflection_info, reflection_events
            scene_time += dt
            waves_to_remove = []
            new_reflected_waves = VGroup()
            new_incident_waves = VGroup()

            if scene_time >= last_emission_time + pulse_interval:
                last_emission_time += pulse_interval
                incident_wave = Line(
                    start=np.array([plane_wave_start_x, -plane_wave_length / 2, 0]),
                    end=np.array([plane_wave_start_x, plane_wave_length / 2, 0]),
                    color=incident_wave_color, stroke_width=wave_stroke_width
                )
                incident_wave.creation_time = scene_time
                incident_wave.is_incident = True
                new_incident_waves.add(incident_wave)

            for wave in mobj:
                if hasattr(wave, 'is_incident') and wave.is_incident:
                    wave.shift(RIGHT * wave_speed * dt)
                    current_x = wave.get_center()[0]
                    if current_x > config.frame_width / 2 + 1:
                         if wave not in waves_to_remove: waves_to_remove.append(wave)
                         continue
                    inc_start = wave.get_start(); inc_end = wave.get_end()
                    intersection_point = get_segment_intersection(inc_start, inc_end, wall_start, wall_end)
                    if intersection_point is not None:
                        is_new_origin = True
                        # Use the main reflection_events list for debouncing
                        for origin_incident_time, origin_pt in reflection_events:
                            if np.linalg.norm(intersection_point - origin_pt) < reflection_debounce_distance and \
                               abs(wave.creation_time - origin_incident_time) < pulse_interval * 0.1:
                                is_new_origin = False; break
                        if is_new_origin:
                            reflection_events.append((wave.creation_time, intersection_point)) # Store event

                            dist_sq = np.sum((intersection_point - wall_center)**2)
                            if dist_sq < best_reflection_info["min_dist_sq"]:
                                best_reflection_info["min_dist_sq"] = dist_sq
                                best_reflection_info["point"] = intersection_point
                            reflected = Circle(
                                radius=0.01, arc_center=intersection_point,
                                stroke_color=reflected_wave_color, stroke_width=wave_stroke_width,
                                fill_opacity=0
                            )
                            reflected.creation_time = scene_time
                            new_reflected_waves.add(reflected)
                else: # Reflected wave
                    time_since_creation = scene_time - wave.creation_time
                    current_radius = time_since_creation * wave_speed
                    if current_radius > max_radius_reflected:
                        if wave not in waves_to_remove: waves_to_remove.append(wave)
                        continue
                    new_appearance = Circle(
                        radius=max(0.01, current_radius), stroke_color=reflected_wave_color,
                        stroke_width=wave_stroke_width, fill_opacity=0
                    ).move_to(wave.get_center())
                    opacity = max(0, 1 - (current_radius / max_radius_reflected)**2)
                    new_appearance.set_stroke(opacity=opacity)
                    wave.become(new_appearance)

            mobj.remove(*waves_to_remove)
            mobj.add(*new_incident_waves)
            mobj.add(*new_reflected_waves)

        # --- Stage 1: Run Wave Animation ---
        all_waves.add_updater(update_reflection_waves)
        self.wait(stage1_duration)
        all_waves.remove_updater(update_reflection_waves)
        self.play(FadeOut(all_waves))
        self.wait(0.5)

        # --- Stage 2 & 3: Show Principle ---
        principle_elements = VGroup() # Group elements to fade later
        if best_reflection_info["point"] is not None:
            rp = best_reflection_info["point"]
            rp_dot = Dot(point=rp, color=BLACK, radius=0.05)

            wall_vector = normalize(wall_end - wall_start)
            wall_line_segment1 = Line(rp, rp + wall_vector * 1.5)
            wall_line_segment2 = Line(rp, rp - wall_vector * 1.5)

            normal_unscaled = np.array([-wall_vector[1], wall_vector[0], 0])
            wall_normal_vec = normalize(normal_unscaled)
            if wall_normal_vec[0] < 0: wall_normal_vec *= -1
            wall_normal_line = Line(rp, rp + wall_normal_vec * 1.5, color=normal_color, stroke_width=2)

            # Add Right Angle symbol between wall and normal
            # Choose one wall segment (e.g., segment1) for the right angle
            right_angle = RightAngle(wall_line_segment1, wall_normal_line, length=0.3, quadrant=(1,1), color=normal_color, stroke_width=2)

            incident_dir = RIGHT
            incident_vec_line = Line(rp, rp - incident_dir * ray_length)

            reflected_dir = normalize(incident_dir - 2 * np.dot(incident_dir, wall_normal_vec) * wall_normal_vec)
            reflected_vec_line = Line(rp, rp + reflected_dir * ray_length)

            incident_ray_disp = Arrow(rp - incident_dir * ray_length, rp, color=ray_color_incident, stroke_width=3, buff=0)
            reflected_ray_disp = Arrow(rp, rp + reflected_dir * ray_length, color=ray_color_reflected, stroke_width=3, buff=0)

            # --- Stage 2 Animation ---
            stage2_group = VGroup(rp_dot, wall_normal_line, right_angle, incident_ray_disp, reflected_ray_disp)
            principle_elements.add(stage2_group)
            self.play(Create(stage2_group), run_time=1.5)
            self.wait(stage2_duration - 1.5)

            # --- Stage 3 Animation ---
            wall_seg_for_inc = wall_line_segment1
            wall_seg_for_ref_start = wall_line_segment2

            # Blue arc: Incident ray to wall segment (clockwise)
            angle_i = Angle(incident_vec_line, wall_line_segment2, radius=0.5, other_angle=True, color=ray_color_incident)
            # Yellow arc: Reflected ray to OPPOSITE wall segment (counter-clockwise)
            angle_r = Angle(reflected_vec_line, wall_line_segment1, radius=0.5, other_angle=False, color=ray_color_reflected)

            label_offset_factor = 0.4
            label_i = MathTex(r"\theta_i", font_size=30).move_to(
                 Angle(incident_vec_line, wall_line_segment2, radius=0.5 + label_offset_factor, other_angle=True).point_from_proportion(0.5)
            ).set_color(ray_color_incident)
            label_r = MathTex(r"\theta_r", font_size=30).move_to(
                 Angle(reflected_vec_line, wall_line_segment1, radius=0.5 + label_offset_factor, other_angle=False).point_from_proportion(0.5)
            ).set_color(ray_color_reflected)

            equation = MathTex(r"\theta_i", "=", r"\theta_r", font_size=36, color=BLACK)
            equation.set_color_by_tex(r"\theta_i", ray_color_incident)
            equation.set_color_by_tex(r"\theta_r", ray_color_reflected)
            equation.next_to(title, DOWN, buff=0.5)

            stage3_group = VGroup(angle_i, angle_r, label_i, label_r, equation)
            principle_elements.add(stage3_group)
            self.play(Create(angle_i), Create(angle_r), run_time=1)
            self.play(Write(label_i), Write(label_r), Write(equation), run_time=1)
            self.wait(stage3_duration - 2)

            # --- Stage 4: Fade Out Principle ---
            self.play(FadeOut(principle_elements), run_time=stage4_duration)
            self.wait(0.5)

            # --- Stage 5: Show Current Densities ---
            current_densities_group = VGroup()
            # Extract unique points from the recorded events
            unique_reflection_points = [event[1] for event in reflection_events]
            # Optional: Further filter points if needed (e.g., remove duplicates if precision issues exist)
            # unique_reflection_points = list({tuple(p): p for p in unique_reflection_points}.values())
            if unique_reflection_points: # Check if any points were stored
                # Use the normalized wall direction vector calculated earlier
                # wall_vector = normalize(wall_end - wall_start) # Already available

                for i, point in enumerate(unique_reflection_points):
                    # Create a thick arrow ALONG the wall
                    arrow_direction = wall_vector # Use the wall's direction
                    arrow_start = point - arrow_direction * 0.2 # Center arrow on point
                    arrow_end = point + arrow_direction * 0.2
                    arrow = Arrow(
                        arrow_start, arrow_end,
                        color=current_density_color,
                        stroke_width=6, # Thicker
                        buff=0,
                        max_tip_length_to_length_ratio=0.3 # Make tip smaller relative to length
                    )
                    # Create label j_1, j_2, ...
                    label = MathTex(f"j_{{{i+1}}}(\\mathbf{{r}})", font_size=30, color=current_density_color) # Larger font
                    # Position label slightly above the arrow's center
                    label.next_to(point, RIGHT, buff=0.15)
                    # Add arrow and label directly to the group
                    current_densities_group.add(arrow, label)
                    if i == 8:
                        break

                # Fade in the entire group at once
                self.play(FadeIn(current_densities_group), run_time=stage5_duration)
                self.wait(2) # Hold the final view

        else:
            self.add(Text("No reflection detected.", font_size=24, color=BLACK))
            self.wait(2)