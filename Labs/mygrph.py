import matplotlib.pyplot as plt
import numpy as np

def draw_mm_graph_paper():
    """Draws exact 1mm, 5mm, and 10mm engineering graph paper."""
    fig, ax = plt.subplots(figsize=(8.27, 11.69), dpi=300) # A4 Size for accurate printing
    
    # The physical paper in your images has 18 major blocks (X) and 25 major blocks (Y)
    x_max, y_max = 180, 250 
    
    ax.set_xlim(0, x_max)
    ax.set_ylim(0, y_max)
    
    # Graph paper ink colors (cyan/light blue)
    major_color = '#7AB8D3' # 1cm (10mm) lines - Darkest
    mid_color = '#A3D1E6'   # 0.5cm (5mm) lines - Medium
    minor_color = '#D1EBF5' # 1mm lines - Lightest
    
    # Draw vertical lines (1mm spacing)
    for x in range(x_max + 1):
        if x % 10 == 0:
            ax.axvline(x, color=major_color, linewidth=1.2)
        elif x % 5 == 0:
            ax.axvline(x, color=mid_color, linewidth=0.8)
        else:
            ax.axvline(x, color=minor_color, linewidth=0.4)
            
    # Draw horizontal lines (1mm spacing)
    for y in range(y_max + 1):
        if y % 10 == 0:
            ax.axhline(y, color=major_color, linewidth=1.2)
        elif y % 5 == 0:
            ax.axhline(y, color=mid_color, linewidth=0.8)
        else:
            ax.axhline(y, color=minor_color, linewidth=0.4)

    # Hide default matplotlib axes/borders
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Add the margin numbers (0-18 on X, 0-25 on Y) just like the printed paper
    for x in range(0, 19):
        ax.text(x * 10, -5, str(x), fontsize=8, ha='center', va='top', color='black')
    for y in range(0, 26):
        ax.text(-3, y * 10, str(y), fontsize=8, ha='right', va='center', color='black')

    return fig, ax

def plot_figure_04_exact():
    fig, ax = plt.subplots(figsize=(8.27, 11.69), dpi=300) # Re-init to use A4 size
    plt.close() # close the blank one, we want to use our custom function
    
    fig, ax = draw_mm_graph_paper()

    # --- DRAWING YOUR HAND-DRAWN AXES ---
    # Based on Fig 4, your Y-axis starts at X=20 (block 2) and X-axis starts at Y=30 (block 3)
    ax.plot([20, 20], [30, 245], color='black', linewidth=1.5) # Y-axis
    ax.plot([20, 175], [30, 30], color='black', linewidth=1.5) # X-axis
    
    # Add axis arrows
    ax.annotate('', xy=(20, 248), xytext=(20, 245), arrowprops=dict(arrowstyle='->', lw=1.5))
    ax.annotate('', xy=(178, 30), xytext=(175, 30), arrowprops=dict(arrowstyle='->', lw=1.5))

    # --- PLOTTING DATA USING PAPER BLOCKS ---
    # To plot here, multiply your graph units by the grid blocks.
    # E.g., in Fig 4, If=0.4 is at block 4 (X=40). If=0.6 is at block 6 (X=60).
    # X multiplier = 100.
    
    if_data = np.array([0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2])
    x_coords = if_data * 100  

    # Y-axis scaling from Fig 4: 
    # y=0.1 is at block 6 (Y=60), y=0.2 is at block 9 (Y=90), y=0.3 is at block 12 (Y=120)
    # The formula for your specific Y scaling is: Y_coord = (y_value * 300) + 30
    
    ia_no_load = np.array([0.4, 0.29, 0.21, 0.14, 0.08, 0.14, 0.20, 0.32, 0.45])
    y_coords_no_load = (ia_no_load * 300) + 30

    # Plot the line (looks hand-drawn)
    ax.plot(x_coords, y_coords_no_load, marker='o', linestyle='-', color='#1f1f1f', 
            linewidth=1.2, markersize=6, markerfacecolor='none', label='No load')

    plt.tight_layout()
    # Save it as a high-res image to print
    plt.savefig('perfect_graph_paper.png', bbox_inches='tight')
    plt.show()

plot_figure_04_exact()