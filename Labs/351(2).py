import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline

# New Data from Table 2
vcc = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
vp = np.array([0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 9, 10, 10, 10])

# Create a smooth curve
X_Y_Spline = make_interp_spline(vcc, vp)
X_smooth = np.linspace(vcc.min(), vcc.max(), 500)
Y_smooth = X_Y_Spline(X_smooth)

# Create the plot
plt.figure(figsize=(10, 6))

# Plot the smooth line and the actual data points
plt.plot(X_smooth, Y_smooth, color='#4472C4', linestyle='-') 
plt.scatter(vcc, vp, color='#4472C4', zorder=5) 

# Add titles and labels
plt.xlabel('Supply Voltage Vcc (V)', fontsize=11)
plt.ylabel('Output Amplitude Vp (V)', fontsize=11)

# Add grid lines
plt.grid(True, linestyle='-', color='lightgrey')
plt.xticks(range(0, 17, 2))
plt.yticks(range(-2, 18, 2))
plt.xlim(0, 16)
plt.ylim(-2, 16)

# Show the graph
plt.show()