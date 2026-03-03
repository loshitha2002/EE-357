import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline

# 1. Data extracted from Table 2 (image_2a38fe)
vcc_volts = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
amplitude_vp = np.array([0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 9, 10, 10, 10])

# 2. Create the Smooth Curve
# The 's' parameter controls smoothness. s=1.5 gives a nice sweeping 
# curve through the points where the amplitude starts to plateau.
spline = UnivariateSpline(vcc_volts, amplitude_vp, s=1.5)

# Generate high-resolution points for a perfectly smooth line
vcc_smooth = np.linspace(vcc_volts.min(), vcc_volts.max(), 500)
amplitude_smooth = spline(vcc_smooth)

# 3. Plotting the Graph
plt.figure(figsize=(9, 6))

# Plot the smooth sweeping curve
plt.plot(vcc_smooth, amplitude_smooth, color='black', linewidth=1.5, label='Smooth Spline Fit')

# Plot the individual data points as open circles
plt.scatter(vcc_volts, amplitude_vp, edgecolors='black', facecolors='none', s=60, zorder=5, label='Data Points')

# 4. Formatting to match the engineering graph paper look
plt.title('VARIATION OF OUTPUT AMPLITUDE VS SUPPLY VOLTAGE (TABLE 2)', fontsize=12, fontweight='bold', loc='left')
plt.xlabel('SUPPLY VOLTAGE, $V_{cc}$ (V)', fontsize=11, fontweight='bold')
plt.ylabel('OUTPUT AMPLITUDE, $V_p$ (V)', fontsize=11, fontweight='bold')

# Set axis limits to frame the data nicely
plt.xlim(-0.5, 16)
plt.ylim(-0.5, 11)

# Create the fine grid that looks like graph paper
plt.grid(True, which='both', linestyle='-', color='lightblue', alpha=0.7)
plt.minorticks_on()
plt.grid(True, which='minor', linestyle=':', color='lightblue', alpha=0.5)

# Add a legend
plt.legend(loc='lower right', fontsize=10)

# Show the plot
plt.show()