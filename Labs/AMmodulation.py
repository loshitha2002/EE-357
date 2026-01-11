import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

# Set plot style
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.figsize'] = (12, 8)

# ============================================================================
# PART 1: Fourier Coefficients and Magnitude Spectra
# ============================================================================

def plot_part1():
    fig, axes = plt.subplots(3, 3, figsize=(18, 10))
    
    # Common parameters
    A_m = 1.0
    f_m = 5.0  # Hz
    A = 1.0
    T0 = 1.0   # Period for pulse/triangle waves
    f0 = 1/T0
    tau = 0.2  # Pulse width for rectangular wave
    
    # Time domain for plotting signals
    t = np.linspace(-2*T0, 2*T0, 1000)
    
    # -----------------------------------------------------
    # (a) x1(t) = A_m * cos(2π f_m t)
    # -----------------------------------------------------
    ax_time = axes[0, 0]
    ax_mag = axes[0, 1]
    ax_phase = axes[0, 2]
    
    x1 = A_m * np.cos(2 * np.pi * f_m * t)
    ax_time.plot(t, x1, 'b-', linewidth=2)
    ax_time.set_title(r'(a) $x_1(t) = A_m \cos(2\pi f_m t)$')
    ax_time.set_xlabel('Time (s)')
    ax_time.set_ylabel('Amplitude')
    ax_time.grid(True)
    ax_time.set_xlim([-0.4, 0.4])
    
    # Frequency domain - discrete spectrum
    freqs = np.array([-f_m, f_m])
    mags = np.array([A_m/2, A_m/2])
    phases = np.array([0, 0])  # Cosine has zero phase
    
    # Magnitude spectrum
    ax_mag.stem(freqs, mags, linefmt='b-', markerfmt='bo', basefmt=' ')
    ax_mag.set_title('Magnitude Spectrum of $x_1(t)$')
    ax_mag.set_xlabel('Frequency (Hz)')
    ax_mag.set_ylabel('Magnitude')
    ax_mag.grid(True)
    ax_mag.set_xlim([-2*f_m, 2*f_m])
    ax_mag.set_ylim([0, A_m/2 * 1.2])
    
    # Phase spectrum
    ax_phase.stem(freqs, phases, linefmt='r-', markerfmt='ro', basefmt=' ')
    ax_phase.set_title('Phase Spectrum of $x_1(t)$')
    ax_phase.set_xlabel('Frequency (Hz)')
    ax_phase.set_ylabel('Phase (radians)')
    ax_phase.grid(True)
    ax_phase.set_xlim([-2*f_m, 2*f_m])
    ax_phase.set_ylim([-np.pi, np.pi])
    
    # -----------------------------------------------------
    # (b) x2(t) - Periodic rectangular pulse train
    # -----------------------------------------------------
    ax_time = axes[1, 0]
    ax_mag = axes[1, 1]
    ax_phase = axes[1, 2]
    
    # Generate rectangular pulse train
    x2 = A * (np.abs((t + T0/2) % T0 - T0/2) < tau/2).astype(float)
    ax_time.plot(t, x2, 'b-', linewidth=2)
    ax_time.set_title('(b) $x_2(t)$ - Rectangular Pulse Train')
    ax_time.set_xlabel('Time (s)')
    ax_time.set_ylabel('Amplitude')
    ax_time.grid(True)
    ax_time.set_xlim([-2*T0, 2*T0])
    ax_time.set_ylim([-0.1, A*1.1])
    
    # Frequency domain - Fourier series coefficients
    # Calculate up to 15 harmonics
    N_harm = 15
    k = np.arange(-N_harm, N_harm+1)
    ck = (A * tau / T0) * np.sinc(k * tau / T0)
    
    # Magnitude spectrum (absolute value)
    ax_mag.stem(k*f0, np.abs(ck), linefmt='b-', markerfmt='bo', basefmt=' ')
    ax_mag.set_title('Magnitude Spectrum of $x_2(t)$')
    ax_mag.set_xlabel('Frequency (Hz)')
    ax_mag.set_ylabel('$|c_k|$')
    ax_mag.grid(True)
    ax_mag.set_xlim([-N_harm*f0, N_harm*f0])
    ax_mag.set_ylim([0, max(np.abs(ck))*1.2])
    
    # Phase spectrum
    phases_ck = np.angle(ck)  # Phase of complex coefficients
    ax_phase.stem(k*f0, phases_ck, linefmt='r-', markerfmt='ro', basefmt=' ')
    ax_phase.set_title('Phase Spectrum of $x_2(t)$')
    ax_phase.set_xlabel('Frequency (Hz)')
    ax_phase.set_ylabel('Phase (radians)')
    ax_phase.grid(True)
    ax_phase.set_xlim([-N_harm*f0, N_harm*f0])
    ax_phase.set_ylim([-np.pi, np.pi])
    
    # -----------------------------------------------------
    # (c) x3(t) - Triangular wave
    # -----------------------------------------------------
    ax_time = axes[2, 0]
    ax_mag = axes[2, 1]
    ax_phase = axes[2, 2]
    
    # Generate triangular wave
    x3 = A * (2 * np.abs(2 * (t/T0 - np.floor(t/T0 + 0.5))) - 1)
    ax_time.plot(t, x3, 'b-', linewidth=2)
    ax_time.set_title('(c) $x_3(t)$ - Triangular Wave')
    ax_time.set_xlabel('Time (s)')
    ax_time.set_ylabel('Amplitude')
    ax_time.grid(True)
    ax_time.set_xlim([-2*T0, 2*T0])
    ax_time.set_ylim([-A*1.1, A*1.1])
    
    # Frequency domain - Fourier series coefficients for triangular wave
    # Only odd harmonics: c_n = (8A/(π²n²)) for n odd (for cosine series)
    # For exponential form: divide by 2
    N_harm = 15
    k = np.arange(-N_harm, N_harm+1)
    ck_tri = np.zeros_like(k, dtype=complex)
    
    for i, n in enumerate(k):
        if n == 0:
            ck_tri[i] = 0  # No DC
        elif n % 2 == 1:  # odd
            # Triangular wave coefficients (real, positive for symmetric wave)
            ck_tri[i] = (4*A) / (np.pi**2 * n**2)
        # else n even: ck = 0
    
    # Magnitude spectrum
    ax_mag.stem(k*f0, np.abs(ck_tri), linefmt='b-', markerfmt='bo', basefmt=' ')
    ax_mag.set_title('Magnitude Spectrum of $x_3(t)$')
    ax_mag.set_xlabel('Frequency (Hz)')
    ax_mag.set_ylabel('$|c_k|$')
    ax_mag.grid(True)
    ax_mag.set_xlim([-N_harm*f0, N_harm*f0])
    ax_mag.set_ylim([0, max(np.abs(ck_tri))*1.2])
    
    # Phase spectrum
    phases_tri = np.angle(ck_tri)
    ax_phase.stem(k*f0, phases_tri, linefmt='r-', markerfmt='ro', basefmt=' ')
    ax_phase.set_title('Phase Spectrum of $x_3(t)$')
    ax_phase.set_xlabel('Frequency (Hz)')
    ax_phase.set_ylabel('Phase (radians)')
    ax_phase.grid(True)
    ax_phase.set_xlim([-N_harm*f0, N_harm*f0])
    ax_phase.set_ylim([-np.pi, np.pi])
    
    plt.tight_layout()
    plt.show()

# ============================================================================
# PART 2: AM Modulation Spectra
# ============================================================================

def plot_part2():
    fig, axes = plt.subplots(3, 2, figsize=(14, 12))
    
    # Common parameters
    f_c = 100.0  # Carrier frequency (Hz)
    A_c = 1.0
    A_m = 0.5
    f_m = 5.0
    A = 1.0
    T0 = 1.0
    f0 = 1/T0
    tau = 0.2
    
    # Frequency range for plotting
    f = np.linspace(-2*f_c, 2*f_c, 2000)
    
    # -----------------------------------------------------
    # (a) y1(t) = A_c * [1 + x1(t)] * cos(2π f_c t)
    # -----------------------------------------------------
    ax_mag = axes[0, 0]
    ax_phase = axes[0, 1]
    
    # Create impulse representation
    # Carrier from DC term: at f = ±f_c with magnitude A_c/2
    # Sidebands from modulation: at f = ±f_c ± f_m with magnitude A_c * A_m / 4
    
    impulse_freqs = np.array([-f_c - f_m, -f_c, -f_c + f_m, 
                              f_c - f_m, f_c, f_c + f_m])
    impulse_mags = np.array([A_c*A_m/4, A_c/2, A_c*A_m/4,
                             A_c*A_m/4, A_c/2, A_c*A_m/4])
    impulse_phases = np.array([0, 0, 0, 0, 0, 0])  # All in phase for standard AM
    
    # Magnitude spectrum
    ax_mag.stem(impulse_freqs, impulse_mags, linefmt='b-', markerfmt='bo', basefmt=' ')
    
    # Add labels for important frequencies
    ax_mag.axvline(x=f_c, color='r', linestyle='--', alpha=0.3, label=f'Carrier $f_c$ = {f_c} Hz')
    ax_mag.axvline(x=-f_c, color='r', linestyle='--', alpha=0.3)
    
    ax_mag.set_title(r'(a) Magnitude Spectrum of $y_1(t) = A_c[1 + A_m\cos(2\pi f_m t)]\cos(2\pi f_c t)$')
    ax_mag.set_xlabel('Frequency (Hz)')
    ax_mag.set_ylabel('Magnitude')
    ax_mag.grid(True)
    ax_mag.set_xlim([-2*f_c, 2*f_c])
    ax_mag.set_ylim([0, A_c/2 * 1.2])
    ax_mag.legend()
    
    # Phase spectrum
    ax_phase.stem(impulse_freqs, impulse_phases, linefmt='r-', markerfmt='ro', basefmt=' ')
    ax_phase.axvline(x=f_c, color='r', linestyle='--', alpha=0.3)
    ax_phase.axvline(x=-f_c, color='r', linestyle='--', alpha=0.3)
    ax_phase.set_title(r'(a) Phase Spectrum of $y_1(t)$')
    ax_phase.set_xlabel('Frequency (Hz)')
    ax_phase.set_ylabel('Phase (radians)')
    ax_phase.grid(True)
    ax_phase.set_xlim([-2*f_c, 2*f_c])
    ax_phase.set_ylim([-np.pi, np.pi])
    
    # -----------------------------------------------------
    # (b) y2(t) = A_c * [1 + x2(t)] * cos(2π f_c t)
    # -----------------------------------------------------
    ax_mag = axes[1, 0]
    ax_phase = axes[1, 1]
    
    # For rectangular pulse train, spectrum consists of carrier + sidebands at harmonics
    # Carrier magnitude: A_c/2 at f = ±f_c
    # Sidebands magnitude: (A_c/2)*|c_k| at f = ±f_c ± k*f0
    
    # Create array of frequencies and magnitudes
    N_harm = 5  # Show 5 harmonics on each side
    impulse_freqs = []
    impulse_mags = []
    impulse_phases = []
    
    # DC term gives carrier
    impulse_freqs.extend([-f_c, f_c])
    impulse_mags.extend([A_c/2, A_c/2])
    impulse_phases.extend([0, 0])
    
    # Modulation terms (from pulse train harmonics)
    ck = (A * tau / T0) * np.sinc(np.arange(-N_harm, N_harm+1) * tau / T0)
    
    for k in range(-N_harm, N_harm+1):
        if k == 0:
            continue  # Already handled as carrier
            
        mag = (A_c/2) * abs(ck[k+N_harm])  # ck array is centered
        phase = np.angle(ck[k+N_harm])
        
        # Lower sideband
        impulse_freqs.append(-f_c + k*f0)
        impulse_mags.append(mag)
        impulse_phases.append(phase)
        # Upper sideband
        impulse_freqs.append(f_c + k*f0)
        impulse_mags.append(mag)
        impulse_phases.append(phase)
    
    impulse_freqs = np.array(impulse_freqs)
    impulse_mags = np.array(impulse_mags)
    impulse_phases = np.array(impulse_phases)
    
    # Sort for cleaner plotting
    sort_idx = np.argsort(impulse_freqs)
    impulse_freqs = impulse_freqs[sort_idx]
    impulse_mags = impulse_mags[sort_idx]
    impulse_phases = impulse_phases[sort_idx]
    
    # Magnitude spectrum
    ax_mag.stem(impulse_freqs, impulse_mags, linefmt='b-', markerfmt='bo', basefmt=' ')
    
    # Add carrier lines
    ax_mag.axvline(x=f_c, color='r', linestyle='--', alpha=0.3, label=f'Carrier $f_c$ = {f_c} Hz')
    ax_mag.axvline(x=-f_c, color='r', linestyle='--', alpha=0.3)
    
    ax_mag.set_title(r'(b) Magnitude Spectrum of $y_2(t) = A_c[1 + x_2(t)]\cos(2\pi f_c t)$')
    ax_mag.set_xlabel('Frequency (Hz)')
    ax_mag.set_ylabel('Magnitude')
    ax_mag.grid(True)
    ax_mag.set_xlim([-2*f_c, 2*f_c])
    ax_mag.set_ylim([0, max(impulse_mags)*1.2])
    ax_mag.legend()
    
    # Phase spectrum
    ax_phase.stem(impulse_freqs, impulse_phases, linefmt='r-', markerfmt='ro', basefmt=' ')
    ax_phase.axvline(x=f_c, color='r', linestyle='--', alpha=0.3)
    ax_phase.axvline(x=-f_c, color='r', linestyle='--', alpha=0.3)
    ax_phase.set_title(r'(b) Phase Spectrum of $y_2(t)$')
    ax_phase.set_xlabel('Frequency (Hz)')
    ax_phase.set_ylabel('Phase (radians)')
    ax_phase.grid(True)
    ax_phase.set_xlim([-2*f_c, 2*f_c])
    ax_phase.set_ylim([-np.pi, np.pi])
    
    # -----------------------------------------------------
    # (c) y3(t) = A_c * [1 + x3(t)] * cos(2π f_c t)
    # -----------------------------------------------------
    ax_mag = axes[2, 0]
    ax_phase = axes[2, 1]
    
    # For triangular wave, similar but harmonics fall off as 1/n²
    impulse_freqs = []
    impulse_mags = []
    impulse_phases = []
    
    # DC term gives carrier
    impulse_freqs.extend([-f_c, f_c])
    impulse_mags.extend([A_c/2, A_c/2])
    impulse_phases.extend([0, 0])
    
    # Modulation terms (from triangle wave harmonics - only odd harmonics)
    N_harm = 5
    for n in range(-N_harm, N_harm+1):
        if n == 0:
            continue
            
        # Only odd harmonics for triangular wave
        if n % 2 == 1:
            mag_tri = (4*A) / (np.pi**2 * n**2)  # From earlier
            mag = (A_c/2) * abs(mag_tri)
            phase = 0  # Real coefficients for triangular wave
            
            # Lower sideband
            impulse_freqs.append(-f_c + n*f0)
            impulse_mags.append(mag)
            impulse_phases.append(phase)
            # Upper sideband
            impulse_freqs.append(f_c + n*f0)
            impulse_mags.append(mag)
            impulse_phases.append(phase)
    
    impulse_freqs = np.array(impulse_freqs)
    impulse_mags = np.array(impulse_mags)
    impulse_phases = np.array(impulse_phases)
    
    # Sort for cleaner plotting
    sort_idx = np.argsort(impulse_freqs)
    impulse_freqs = impulse_freqs[sort_idx]
    impulse_mags = impulse_mags[sort_idx]
    impulse_phases = impulse_phases[sort_idx]
    
    # Magnitude spectrum
    ax_mag.stem(impulse_freqs, impulse_mags, linefmt='b-', markerfmt='bo', basefmt=' ')
    
    # Add carrier lines
    ax_mag.axvline(x=f_c, color='r', linestyle='--', alpha=0.3, label=f'Carrier $f_c$ = {f_c} Hz')
    ax_mag.axvline(x=-f_c, color='r', linestyle='--', alpha=0.3)
    
    ax_mag.set_title(r'(c) Magnitude Spectrum of $y_3(t) = A_c[1 + x_3(t)]\cos(2\pi f_c t)$')
    ax_mag.set_xlabel('Frequency (Hz)')
    ax_mag.set_ylabel('Magnitude')
    ax_mag.grid(True)
    ax_mag.set_xlim([-2*f_c, 2*f_c])
    ax_mag.set_ylim([0, max(impulse_mags)*1.2])
    ax_mag.legend()
    
    # Phase spectrum
    ax_phase.stem(impulse_freqs, impulse_phases, linefmt='r-', markerfmt='ro', basefmt=' ')
    ax_phase.axvline(x=f_c, color='r', linestyle='--', alpha=0.3)
    ax_phase.axvline(x=-f_c, color='r', linestyle='--', alpha=0.3)
    ax_phase.set_title(r'(c) Phase Spectrum of $y_3(t)$')
    ax_phase.set_xlabel('Frequency (Hz)')
    ax_phase.set_ylabel('Phase (radians)')
    ax_phase.grid(True)
    ax_phase.set_xlim([-2*f_c, 2*f_c])
    ax_phase.set_ylim([-np.pi, np.pi])
    
    plt.tight_layout()
    plt.show()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("Generating Fourier coefficient plots for Part 1...")
    plot_part1()
    
    print("\nGenerating AM modulation spectrum plots for Part 2...")
    plot_part2()
    
    print("\nDone! Check the plots.")