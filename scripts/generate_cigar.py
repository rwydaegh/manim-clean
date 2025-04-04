import matplotlib.pyplot as plt
import numpy as np
import os

# --- Parameters ---
output_dir = "media/images/tx_beamforming_arcs"
output_filename = "cigar_pattern.svg"
height = 3.0  # Desired height (max radius) of the cigar lobe
power = 100   # Power for cosine function (MUCH higher = thinner cigar)
num_points = 500 # Increased points for smoother curve with high power
outline_color = 'green'
fill_color = 'green'
fill_alpha = 0.15 # Faint fill

# --- Calculations ---
# Generate angles specifically for the main lobe (-pi/2 to pi/2 relative to broadside)
# This avoids calculating points where radius should be zero anyway.
num_lobe_points = num_points // 2 # Points for just the lobe
theta_relative = np.linspace(-np.pi / 2, np.pi / 2, num_lobe_points)

# Calculate radius based on powered cosine
# Ensure cosine argument is non-negative before raising to power
cos_vals = np.cos(theta_relative)
# Add small epsilon to prevent potential issues with cos(pi/2) being slightly non-zero due to float precision
# Ensure base is strictly non-negative for power calculation
radius = height * (np.maximum(0, cos_vals)**power)

# Absolute angle 't' corresponding to theta_relative, centered around pi/2 (UP)
t = theta_relative + np.pi / 2

# Convert polar (radius, t) to Cartesian coordinates
x = radius * np.cos(t)
y = radius * np.sin(t)

# Ensure the node is exactly at (0,0) by removing tiny residual y values near the node
y[np.abs(theta_relative) > (np.pi/2 - 0.01)] = 0
x[np.abs(theta_relative) > (np.pi/2 - 0.01)] = 0

# Create the plot
# Estimate figure size based on calculated max x/y to maintain aspect ratio
max_x_abs = np.max(np.abs(x)) if len(x) > 0 else 0.1
max_y = np.max(y) if len(y) > 0 else 0.1
# Add buffer to prevent clipping, especially for thin shapes
fig_width = max(max_x_abs * 2.5, 0.5) # Ensure minimum width
fig_height = max(max_y * 1.2, 0.5)  # Ensure minimum height
fig, ax = plt.subplots(figsize=(fig_width, fig_height)) # Use calculated aspect ratio

# Plot the outline
ax.plot(x, y, color=outline_color, linewidth=1)

# Fill the shape
ax.fill(x, y, color=fill_color, alpha=fill_alpha, closed=True) # Explicitly close for fill

# --- Appearance ---
ax.set_aspect('equal', adjustable='box')
ax.axis('off') # Turn off axes
fig.patch.set_alpha(0) # Make figure background transparent
ax.patch.set_alpha(0) # Make axes background transparent

# Adjust plot limits slightly to avoid clipping
# Ensure y starts from 0 or slightly below
min_y_limit = min(np.min(y) - 0.1, -0.1)
ax.set_xlim([np.min(x) - 0.1, np.max(x) + 0.1])
ax.set_ylim([min_y_limit, np.max(y) + 0.1])


# --- Save ---
output_path = os.path.join(output_dir, output_filename)
# Create the directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)
try:
    plt.savefig(output_path, format='svg', transparent=True, bbox_inches='tight', pad_inches=0)
    print(f"Cigar shape saved to {output_path}")
except Exception as e:
    print(f"Error saving SVG: {e}")

# plt.show() # Uncomment to display locally if needed