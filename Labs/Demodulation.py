import numpy as np
import matplotlib.pyplot as plt
from scipy import signal


def simulate_synchronous_am_demodulation(
	*,
	A_m: float = 1.0,
	f_m: float = 1_000.0,
	A_c: float = 2.0,
	f_c: float = 100_000.0,
	mu: float = 0.8,
	fs: float = 1_000_000.0,
	duration: float = 0.005,
	lpf_cutoff: float = 5_000.0,
	butter_order: int = 2,
):
	"""Simulate AM generation and synchronous (coherent) demodulation.

	Notes
	-----
	The lab handout states:
	  s(t) = [A_c + m(t)] cos(2π f_c t)
	but also separately specifies a modulation index μ=0.8 while using A_m=1 V
	and A_c=2 V. In standard AM (DSB-LC), μ is typically defined with a
	*normalized* message: s(t)=A_c(1+μ m_norm(t))cos(2π f_c t), where |m_norm|<=1.

	This implementation uses that standard definition so μ is exactly the
	modulation index.
	"""

	if fs <= 2 * max(f_c * 2, lpf_cutoff):
		raise ValueError("Sampling frequency fs is too low for the chosen f_c/cutoff.")
	if mu <= 0:
		raise ValueError("Modulation index mu must be > 0.")
	if lpf_cutoff >= fs / 2:
		raise ValueError("LPF cutoff must be below Nyquist (fs/2).")

	t = np.arange(0.0, duration, 1.0 / fs)

	# 1) Message and carrier
	m = A_m * np.cos(2 * np.pi * f_m * t)
	c = A_c * np.cos(2 * np.pi * f_c * t)

	# 2) AM signal: s(t) = A_c(1 + μ m_norm(t))cos(2π f_c t)
	m_norm = m / A_m
	s = A_c * (1.0 + mu * m_norm) * np.cos(2 * np.pi * f_c * t)

	# 3) Synchronous demodulation
	lo = np.cos(2 * np.pi * f_c * t)  # same frequency + phase as carrier
	v = s * lo

	# Low-pass filter (2nd order Butterworth, cutoff 5 kHz)
	b, a = signal.butter(butter_order, lpf_cutoff / (fs / 2), btype="low")
	v_lpf = signal.filtfilt(b, a, v)

	# Recover message:
	# v_lpf ≈ 0.5*A_c*(1 + μ m_norm(t))  -> remove DC and scale
	m_hat = A_m * (2.0 / (A_c * mu)) * (v_lpf - 0.5 * A_c)

	return {
		"t": t,
		"m": m,
		"c": c,
		"s": s,
		"lo": lo,
		"v": v,
		"v_lpf": v_lpf,
		"m_hat": m_hat,
		"params": {
			"A_m": A_m,
			"f_m": f_m,
			"A_c": A_c,
			"f_c": f_c,
			"mu": mu,
			"fs": fs,
			"duration": duration,
			"lpf_cutoff": lpf_cutoff,
			"butter_order": butter_order,
		},
	}


def plot_results(results: dict) -> None:
	plt.style.use("seaborn-v0_8-darkgrid")
	plt.rcParams["figure.figsize"] = (12, 10)

	t = results["t"]
	m = results["m"]
	c = results["c"]
	s = results["s"]
	v = results["v"]
	m_hat = results["m_hat"]
	params = results["params"]

	fig, axes = plt.subplots(5, 1, sharex=True)

	axes[0].plot(t * 1e3, m, linewidth=2)
	axes[0].set_title(r"Message signal $m(t)=A_m\cos(2\pi f_m t)$")
	axes[0].set_ylabel("V")

	axes[1].plot(t * 1e3, c, linewidth=1)
	axes[1].set_title(r"Carrier signal $c(t)=A_c\cos(2\pi f_c t)$")
	axes[1].set_ylabel("V")

	axes[2].plot(t * 1e3, s, linewidth=1)
	axes[2].set_title(r"AM signal $s(t)=A_c(1+\mu m_{norm}(t))\cos(2\pi f_c t)$")
	axes[2].set_ylabel("V")

	axes[3].plot(t * 1e3, v, linewidth=1)
	axes[3].set_title(r"Mixer output $v(t)=s(t)\,c_{LO}(t)$")
	axes[3].set_ylabel("V")

	axes[4].plot(t * 1e3, m, label="Original m(t)", linewidth=2)
	axes[4].plot(t * 1e3, m_hat, label=r"Demodulated $\hat{m}(t)$", linewidth=2, alpha=0.85)
	axes[4].set_title(r"Recovered message after 2nd-order Butterworth LPF")
	axes[4].set_xlabel("Time (ms)")
	axes[4].set_ylabel("V")
	axes[4].legend(loc="upper right")

	fig.suptitle(
		"Synchronous AM Demodulation (Coherent Detector)\n"
		+ f"A_m={params['A_m']}V, f_m={params['f_m']/1e3:.1f}kHz, "
		+ f"A_c={params['A_c']}V, f_c={params['f_c']/1e3:.1f}kHz, "
		+ f"μ={params['mu']}, LPF={params['lpf_cutoff']/1e3:.1f}kHz",
		y=0.995,
		fontsize=12,
	)

	plt.tight_layout()
	plt.show()


def main() -> None:
	results = simulate_synchronous_am_demodulation()
	plot_results(results)


if __name__ == "__main__":
	main()

