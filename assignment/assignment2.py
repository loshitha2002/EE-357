import numpy as np
import matplotlib.pyplot as plt

# 1. Define the Input Sequence
bits = np.array([1, 0, 1, 0, 0, 0, 1, 1, 0])

# Simulation parameters
bit_duration = 1.0
samples_per_bit = 100
t = np.linspace(0, len(bits) * bit_duration, len(bits) * samples_per_bit)

# Prepare empty arrays for signals
unipolar_nrz = np.zeros_like(t)
unipolar_rz = np.zeros_like(t)
bipolar_rz = np.zeros_like(t)
manchester_nrz = np.zeros_like(t)

# 2. Logic for Each Encoding Scheme
last_bipolar = -1  # Keep track of last '1' polarity for AMI (starts assuming prev was -)

for i, bit in enumerate(bits):
    # Indices for the current bit in the time array
    start = i * samples_per_bit
    end = (i + 1) * samples_per_bit
    half = start + samples_per_bit // 2
    
    # --- Unipolar NRZ ---
    # 1 = +1V, 0 = 0V (Full duration)
    if bit == 1:
        unipolar_nrz[start:end] = 1.0
    else:
        unipolar_nrz[start:end] = 0.0

    # --- Unipolar RZ ---
    # 1 = +1V (First half), 0 = 0V
    if bit == 1:
        unipolar_rz[start:half] = 1.0
        unipolar_rz[half:end] = 0.0
    else:
        unipolar_rz[start:end] = 0.0

    # --- Bipolar RZ (AMI) ---
    # 1 = Alternating +0.5 / -0.5 (First half), 0 = 0V
    if bit == 1:
        last_bipolar *= -1  # Flip polarity
        bipolar_rz[start:half] = last_bipolar * 0.5
        bipolar_rz[half:end] = 0.0
    else:
        bipolar_rz[start:end] = 0.0
        
    # --- Manchester NRZ ---
    # 1 = High->Low (+0.5 -> -0.5)
    # 0 = Low->High (-0.5 -> +0.5)
    if bit == 1:
        manchester_nrz[start:half] = 0.5
        manchester_nrz[half:end] = -0.5
    else:
        manchester_nrz[start:half] = -0.5
        manchester_nrz[half:end] = 0.5

# 3. Plotting
fig, axs = plt.subplots(4, 1, figsize=(10, 12), sharex=True)
plt.subplots_adjust(hspace=0.5)

signals = [unipolar_nrz, unipolar_rz, bipolar_rz, manchester_nrz]
titles = ['Unipolar NRZ', 'Unipolar RZ', 'Bipolar RZ (AMI)', 'Manchester NRZ']
colors = ['blue', 'green', 'red', 'purple']

for ax, signal, title, color in zip(axs, signals, titles, colors):
    ax.plot(t, signal, color=color, linewidth=2)
    ax.set_title(title, fontsize=14, loc='left')
    ax.grid(True, which='both', linestyle='--', alpha=0.6)
    ax.set_ylabel('Amplitude (V)')
    
    # Set y-limits slightly wider to see the waveform clearly
    if "Bipolar" in title or "Manchester" in title:
        ax.set_ylim(-0.75, 0.75)
        ax.axhline(0, color='black', linewidth=1) # Draw zero line
    else:
        ax.set_ylim(-0.2, 1.2)
    
    # Draw vertical bit boundaries and bit labels
    for i in range(len(bits)):
        ax.axvline(x=(i+1)*bit_duration, color='gray', linestyle=':', alpha=0.5)
        # Label the bit value at the top of the subplot
        ax.text((i + 0.5) * bit_duration, ax.get_ylim()[1] * 0.85, str(bits[i]), 
                horizontalalignment='center', fontweight='bold')

plt.xlabel('Time (s)', fontsize=12)
plt.suptitle(f'Signaling Waveforms for Input: {bits}', fontsize=16)
plt.show()