import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline

# 1. Data extracted exactly from your hand-drawn graph (image_342e40)
vcc_volts = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
amplitude_vp = np.array([0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 8, 8, 8, 8, 9, 10])

# 2. Create the "Hand-Drawn" Smooth Curve
# UnivariateSpline acts like a French Curve. The 's' parameter controls the smoothness.
# s=0.05 allows it to gently sweep through the points without oscillating.
spline = UnivariateSpline(vcc_volts, amplitude_vp, s=2)

# Generate high-resolution points for a perfectly smooth line
vcc_smooth = np.linspace(vcc_volts.min(), vcc_volts.max(), 500)
amplitude_smooth = spline(vcc_smooth)

# 3. Plotting the Graph
plt.figure(figsize=(9, 6))

# Plot the smooth curve (The sweeping line)
plt.plot(vcc_smooth, amplitude_smooth, color='black', linewidth=1.5, label='Smooth Spline Fit')

# Plot the individual data points (The circles)
# facecolors='none' makes them look exactly like the open circles in your drawing!
plt.scatter(vcc_volts, amplitude_vp, edgecolors='black', facecolors='none', s=60, zorder=5, label='Data Points')

# 4. Formatting to match your image
plt.title('FIGURE 4: VARIATION OF OUTPUT AMPLITUDE VS SUPPLY VOLTAGE', fontsize=12, fontweight='bold', loc='left')
plt.xlabel('SUPPLY VOLTAGE (V)', fontsize=11, fontweight='bold')
plt.ylabel('OUTPUT AMPLITUDE (V)', fontsize=11, fontweight='bold')

# Set axis limits to fit all data
plt.xlim(-0.5, 17)
plt.ylim(-2, 11)

# Create a fine grid that looks like graph paper
plt.grid(True, which='both', linestyle='-', color='lightblue', alpha=0.7)
plt.minorticks_on()
plt.grid(True, which='minor', linestyle=':', color='lightblue', alpha=0.5)

# Show the plot
plt.show()