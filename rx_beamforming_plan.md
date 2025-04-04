# Rx Beamforming Animation Plan (Revised)

This plan outlines the steps to create a Manim animation visualizing Rx beamforming using 3 MPCs and morphing a summed heatmap to show phase alignment.

```mermaid
graph TD
    A[Start] --> B(Setup Scene: Box, Rx, Constants - num_mpc=3, Spaced AoAs);
    B --> C{Time Domain};
    C --> D[Define 3 MPC Sources (Implicit)];
    D --> E[Animate Spherical Waves Sequentially (MPC 1, 2, 3)];
    E --> F[Waves Impinge on Rx (Random Phases)];
    F --> G{Transition: Time -> Frequency};
    G --> H[Fade Out Last Time Domain Waves];
    H --> I[Wait Briefly];
    I --> J{Frequency Domain: Summed Field Morph};
    J --> K[Calculate Initial Complex Field Sum (Grid)];
    K --> L[Generate Initial Summed Heatmap Image];
    L --> M[Display Initial Heatmap];
    M --> N[Define ValueTracker: alignment (0 to 1)];
    N --> O[Add Updater to Heatmap Image];
    O --> P[Updater: Recalculate Summed Field(alignment)];
    P --> Q[Updater: Regenerate/Update Heatmap Image Data];
    Q --> R[Animate alignment Tracker (0 -> 1)];
    R --> S[Wait for Morph to Complete];
    S --> T{Final Hotspot Emphasis};
    T --> U[Flash Rx Dot];
    U --> V[Hold Final State];
    V --> W[End];

    subgraph TD [Time Domain]
        direction LR
        D
        E
        F
    end

     subgraph FD_Morph [Frequency Domain - Summed Field Morph]
        direction LR
        K
        L
        M
        N
        O
        P
        Q
        R
        S
     end
```

### Detailed Steps:

*   [ ] **1. Setup Scene:**
    *   [ ] Create a Manim `Scene`.
    *   [ ] Define a white `Rectangle` (the "box") centered on the screen.
    *   [ ] Place a `Dot` in the center of the box representing the Receiver (Rx).
    *   [ ] Define constants: `num_mpc = 3`, wave speed, wave frequency (for `k`), amplitude `A`, box dimensions, animation timings.
    *   [ ] Define 3 distinct Angle of Arrival (AoA) directions (e.g., `[PI * 3/4, PI * 1/4, PI * 7/4]`) ensuring >= 30 deg spacing. Recalculate `mpc_source_positions`.
    *   [ ] Ensure `mpc_initial_phases` and `mpc_time_delays` are sized for 3 MPCs.
    *   [ ] Add a title "Hotspots".

*   [ ] **2. Time Domain - Incoming Waves (Sequential):**
    *   [ ] Implement wave generation (`generate_wave_set_rx`).
    *   [ ] Implement wave update logic (`update_wave_group`) using `set_points`.
    *   [ ] Loop `for mpc_index in range(num_mpc):`
        *   Create `VGroup` for current MPC waves.
        *   Setup time tracker for the current MPC.
        *   Add updater using `lambda` to capture loop variables and pass tracker.
        *   Add group to scene.
        *   Show MPC label.
        *   `self.wait(time_domain_duration_per_mpc)`.
        *   Remove updater.
        *   Fade out waves and label.

*   [ ] **3. Transition: Time to Frequency:**
    *   [ ] `self.wait()` briefly.

*   [ ] **4. Frequency Domain - Summed Heatmap Morph:**
    *   [ ] Define `calculate_summed_field(grid_points, alignment_value)`:
        *   Takes grid points and alignment factor (0 to 1).
        *   Calculates phase adjustments needed for alignment at Rx (`rotation_angles`).
        *   Loops through each MPC:
            *   Calculates distance `r` from source to each grid point.
            *   Calculates initial phase at each grid point: `phi_initial = k * r + initial_phase`.
            *   Calculates adjusted phase at each grid point: `phi_adjusted = phi_initial + alignment_value * rotation_angle`.
            *   Calculates complex field for this MPC: `A * exp(j * phi_adjusted)`.
        *   Sums the complex fields from all 3 MPCs for each grid point.
        *   Returns the magnitude (or magnitude squared for intensity) of the summed complex field at each grid point.
    *   [ ] Calculate `rotation_angles` needed for alignment (phase at Rx for each MPC).
    *   [ ] Calculate initial summed field magnitude grid by calling `calculate_summed_field` with `alignment_value = 0`.
    *   [ ] Generate initial heatmap `ImageMobject` using Matplotlib from the magnitude grid.
    *   [ ] Add initial heatmap to the scene (`FadeIn` or `Create`).
    *   [ ] Create `alignment_tracker = ValueTracker(0)`.
    *   [ ] Define `heatmap_updater(heatmap_image_mobject)`:
        *   Get `alignment_value = alignment_tracker.get_value()`.
        *   Call `calculate_summed_field` with current `alignment_value`.
        *   Generate new Matplotlib image buffer from the result.
        *   Convert buffer to NumPy array `new_image_data`.
        *   Update the `ImageMobject`: `heatmap_image_mobject.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])`, `heatmap_image_mobject.set_data(new_image_data)`.
    *   [ ] Add `heatmap_updater` to the heatmap `ImageMobject`.
    *   [ ] Animate the tracker: `self.play(alignment_tracker.animate.set_value(1), run_time=...)`.

*   [ ] **5. Final Hotspot Emphasis:**
    *   [ ] After the tracker animation, play `Flash(rx_dot, ...)` animation.

*   [ ] **6. Hold and End:**
    *   [ ] `self.wait(final_hold_duration)`.