"""
Visualization functions for WeightedPOD results.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from matplotlib import colormaps               
from matplotlib.colors import Normalize
import seaborn as sns

def plot_energy_spectrum(pod_object, method='snapshots', n_modes=None, figsize=(10, 5)):
    """
    Plot energy spectrum of POD modes, including individual and cumulative energy content.
    
    Parameters:
    -----------
    pod_object : object
        Object containing computed POD results
    method : str
        Either 'snapshots' or 'svd' to choose the POD method
    n_modes : int, optional
        Number of modes to plot. Defaults to min(15, total modes).
    figsize : tuple, optional
        Figure size. Default is (10, 5).
    """
    
    # Check which method to use and validate the corresponding attributes
    if method == 'snapshots':
        if not hasattr(pod_object, 'energy_content'):
            raise ValueError("POD not computed yet. Run compute_pod_method_of_snapshots() first")
        energy_content = pod_object.energy_content
        # Check for cumulative energy attribute
        if hasattr(pod_object, 'cumulative_energy'):
            cumulative_energy = pod_object.cumulative_energy
        else:
            # Calculate cumulative energy if not available
            cumulative_energy = np.cumsum(energy_content)
        filename_suffix = ""
    elif method == 'svd':
        if not hasattr(pod_object, 'energy_content_svd'):
            raise ValueError("SVD-based POD not computed yet. Run compute_pod_svd() first")
        energy_content = pod_object.energy_content_svd
        # Check for cumulative energy attribute
        if hasattr(pod_object, 'cumulative_energy_svd'):
            cumulative_energy = pod_object.cumulative_energy_svd
        else:
            # Calculate cumulative energy if not available
            cumulative_energy = np.cumsum(energy_content)
        filename_suffix = "_svd"
    else:
        raise ValueError("Method must be either 'snapshots' or 'svd'")
    
    max_modes = n_modes or min(15, len(energy_content))
    max_modes = min(max_modes, len(energy_content))
    
    # Use a clean and modern plotting style
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize, sharex=True)
    
    # Style axes spines
    for ax in [ax1, ax2]:
        for spine in ax.spines.values():
            spine.set_edgecolor('black')
            spine.set_linewidth(2)
    
    bar_color = '#0072B2'      # Blue for bars
    line_color = '#009E73'     # Green for lines
    
    highlight_colors = {
        90: '#FCAE91',
        95: '#FB6A4A',
        99: '#CB181D'
    }
    
    # Individual energy content bar plot
    ax1.bar(range(1, max_modes + 1), energy_content[:max_modes], color=bar_color)
    ax1.set_xlabel('POD Modes', fontsize=10)
    ax1.set_ylabel('Energy Content (%)', fontsize=10)
   # ax1.set_title(f'Individual Energy Content ({method.upper()})')
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='y', direction='out', length=4, width=1, color='black')
    
    # Cumulative energy content line plot
    ax2.plot(range(1, max_modes + 1), cumulative_energy[:max_modes], 'o-', 
             color=line_color, linewidth=2, markersize=4)
    for y_val, color in highlight_colors.items():
        ax2.axhline(y=y_val, color=color, linestyle='--', alpha=0.7, label=f'{y_val}%')
    ax2.set_xlabel('POD Modes', fontsize=10)
    ax2.set_ylabel('Cumulative Energy Content (%)', fontsize=10)
 #    ax2.set_title(f'Cumulative Energy Content ({method.upper()})')
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='y', direction='out', length=4, width=1, color='black')
    ax2.legend()
    
    plt.tight_layout()
    
    # Save with method-specific filenames
    plt.savefig(f"pod_energy{filename_suffix}.tiff", dpi=600)
    plt.savefig(f"pod_energy{filename_suffix}.pdf", dpi=600)
    plt.show()
    
    # Print summary statistics
    print(f"\nEnergy Statistics ({method.upper()} method):")
    print(f"First mode captures: {energy_content[0]:.2f}% of energy")
    if len(energy_content) >= 5:
        print(f"First 5 modes capture: {cumulative_energy[4]:.2f}% of energy")
    
    for threshold in [90, 95, 99]:
        modes_needed = np.where(cumulative_energy >= threshold)[0]
        if modes_needed.size > 0:
            print(f"Need {modes_needed[0] + 1} modes for {threshold}% energy")
    
    return fig

def plot_modes(pod_object, mode_indices, method='snapshots', figsize=(12, 8)):
    """
    Plot spatial POD modes.
    
    Parameters:
    -----------
    pod_object : WeightedPOD
        Computed POD object
    mode_indices : list
        List of mode indices to plot
    method : str
        Either 'snapshots' or 'svd' to choose the POD method
    figsize : tuple
        Figure size
    """
    
    # Check which method to use and validate the corresponding attributes
    if method == 'snapshots':
        if not hasattr(pod_object, 'phi_pod'):
            raise ValueError("POD not computed yet. Run compute_pod_method_of_snapshots() first")
        modes = pod_object.phi_pod
        # Check if energy_content exists for snapshots method
        if hasattr(pod_object, 'energy_content'):
            energy = pod_object.energy_content
        else:
            energy = None
    elif method == 'svd':
        if not hasattr(pod_object, 'phi_pod_svd'):
            raise ValueError("SVD-based POD not computed yet. Run the corresponding SVD method first")
        modes = pod_object.phi_pod_svd
        # Check if energy_content_svd exists for SVD method
        if hasattr(pod_object, 'energy_content_svd'):
            energy = pod_object.energy_content_svd
        elif hasattr(pod_object, 'energy_content'):
            energy = pod_object.energy_content
        else:
            energy = None
    else:
        raise ValueError("Method must be either 'snapshots' or 'svd'")
    
    n_modes = len(mode_indices)
    fig, axes = plt.subplots(1, n_modes, figsize=figsize)
    if n_modes == 1:
        axes = [axes]
    
    for i, mode_idx in enumerate(mode_indices):
        # Create scatter plot
        im = axes[i].scatter(range(len(modes[:, mode_idx])), 
                           modes[:, mode_idx], 
                           c=modes[:, mode_idx], 
                           cmap='RdBu_r', s=1)
        
        # Set title with energy content if available
        if energy is not None and mode_idx < len(energy):
            title = f'Mode {mode_idx+1} ({energy[mode_idx]:.2f}%)'
        else:
            title = f'Mode {mode_idx+1}'
        
        axes[i].set_title(title)
        axes[i].set_xlabel('Spatial Point')
        axes[i].set_ylabel('Mode Amplitude')
        
        # Add colorbar
        plt.colorbar(im, ax=axes[i])
        
        # Style the axes
        for spine in axes[i].spines.values():
            spine.set_linewidth(1.5)
        axes[i].tick_params(axis='both', which='major', labelsize=10)
        axes[i].grid(True, ls='--', alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    return fig


def plot_reconstruction(original, reconstructed, snapshot_idx=0, figsize=(12, 5)):
    """
    Plot comparison between original and reconstructed fields.
    
    Parameters:
    -----------
    original : numpy.ndarray
        Original field
    reconstructed : numpy.ndarray
        Reconstructed field  
    snapshot_idx : int
        Snapshot index to plot
    figsize : tuple
        Figure size
    """
    fig, axes = plt.subplots(1, 3, figsize=figsize)
    
    # Original
    axes[0].plot(original[:, snapshot_idx])
    axes[0].set_title('Original')
    axes[0].set_xlabel('Spatial Point')
    axes[0].set_ylabel('Field Value')
    axes[0].grid(True, alpha=0.3)
    
    # Reconstructed
    axes[1].plot(reconstructed[:, snapshot_idx])
    axes[1].set_title('Reconstructed')
    axes[1].set_xlabel('Spatial Point')
    axes[1].set_ylabel('Field Value')
    axes[1].grid(True, alpha=0.3)
    
    # Error
    error = original[:, snapshot_idx] - reconstructed[:, snapshot_idx]
    axes[2].plot(error)
    axes[2].set_title('Error')
    axes[2].set_xlabel('Spatial Point')
    axes[2].set_ylabel('Error')
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_temporal_coefficient(pod_object, mode_idx, angles, method='snapshots'):
    """
    Plots temporal coefficient for a specific POD mode over given angles.
    
    Parameters:
        pod_object : WeightedPOD object 
        mode_idx   : int, which mode to plot (0-based indexing)
        angles     : numpy array of angle values (e.g., [5, 10, 15, ..., 90])
        method     : str, either 'snapshots' or 'svd' to choose the POD method
    """
    
    # Check which method to use and validate the corresponding attribute
    if method == 'snapshots':
        if not hasattr(pod_object, 'a_pod'):
            raise ValueError("POD not computed yet. Run compute_pod_method_of_snapshots() first")
        coefficients = pod_object.a_pod
    elif method == 'svd':
        if not hasattr(pod_object, 'a_pod_svd'):
            raise ValueError("SVD-based POD not computed yet. Run the corresponding SVD method first")
        coefficients = pod_object.a_pod_svd
    else:
        raise ValueError("Method must be either 'snapshots' or 'svd'")
    
    # Create the plot
    plt.figure()
    plt.plot(angles,
             coefficients[mode_idx, :],
             'o-',
             color='red')
    
    # Style the axes
    ax = plt.gca()
    for spine in ax.spines.values():
        spine.set_linewidth(2)
    
    # Major tick parameters
    ax.tick_params(
        axis='both',          # apply to both axes
        which='major',        # major ticks
        labelsize=12,         # font size
        width=2,              # tick width
        length=6              # tick length
    )
    
    # Minor ticks
    ax.minorticks_on()        
    ax.tick_params(
        axis='both',
        which='minor',
        length=4
    )
    
    # Labels and grid
    plt.xlabel('Angle [°]')
    plt.ylabel(f'Mod {mode_idx+1} Coefficient')  # +1 for 1-based display
    plt.grid(True, ls='--', alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    return plt.gcf()
def plot_allModes(pod_object, angles, Re, method='snapshots'):
    """
    Plots the first 16 POD mode coefficients over given angles.
    
    Parameters:
        pod_object : WeightedPOD object 
        angles     : numpy array of angle values (e.g., [5, 10, 15, ..., 90])
        Re         : float, Reynolds number (used in filename)
        method     : str, either 'snapshots' or 'svd' to choose the POD method
    """
    
    if method == 'snapshots':
        if not hasattr(pod_object, 'a_pod'):
            raise ValueError("POD not computed yet. Run compute_pod_method_of_snapshots() first")
        coefficients = pod_object.a_pod
        filename_suffix = "_snapshots"
        
    elif method == 'svd':
        if not hasattr(pod_object, 'a_pod_svd'):
            raise ValueError("SVD-based POD not computed yet. Run the corresponding SVD method first")
        coefficients = pod_object.a_pod_svd
        filename_suffix = "_svd"
    else:
        raise ValueError("Method must be either 'snapshots' or 'svd'")
    
    def style_axes(ax):
        """Apply consistent styling to axes"""
        for spine in ax.spines.values():
            spine.set_linewidth(2)
        ax.tick_params(axis='both', which='major',
                       labelsize=12, width=2, length=6)
        ax.minorticks_on()
        ax.tick_params(axis='both', which='minor', length=4)
        ax.grid(True, ls='--', alpha=0.3)
    
    # Configuration for subplot layout
    n_show = 16
    rows, cols = 4, 4
    
    # Calculate the "size" of each mode as the maximum absolute coefficient value
    # This gives an idea of how strong each mode is across all angles
    mode_size = np.max(np.abs(coefficients[:n_show, :]), axis=1)  # shape (n_show,)
    
    # Normalize mode_size values between 0 and 1 for coloring
    norm = Normalize(vmin=mode_size.min(), vmax=mode_size.max())
    cmap = colormaps['viridis_r']
    
    # Create the subplot grid
    fig, axes = plt.subplots(
        rows, cols,
        figsize=(cols * 4, rows * 2.5),
        sharex=True,
        constrained_layout=True
    )
    
    # Plot each mode
    for k, ax in enumerate(axes.ravel()):
        if k >= n_show:
            ax.set_visible(False)
            continue
        
        # Get a color for this mode based on normalized mode size
        colour = cmap(norm(mode_size[k]))
        
        # Plot mode coefficient vs angle, with circle markers and colored line
        ax.plot(
            angles, coefficients[k, :],
            marker='o', lw=1.5, color=colour
        )
        ax.set_ylabel(f'Mod {k+1} coeff')
        
        style_axes(ax)
    
    # Add X-labels to the bottom row
    for ax in axes[-1]:
        ax.set_xlabel('Angle [°]')
    
    # Add a colorbar to show how color maps to mode size
    sm = cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=axes, shrink=0.85, pad=0.02)
    cbar.set_label('Mode Size (Max |coeff|)', rotation=270, labelpad=20)
    
    # Save and show the plot
    save_path = f"ModesFrom1To16_Re_{Re}{filename_suffix}.pdf"
    fig.savefig(save_path, bbox_inches="tight")
    plt.show()
    
    return fig


def plot_reconstructionError_snapshots(pod_object,num_modes,Ux_dict,Re):
    """
    Parameters:
        pod_object : POD object with .phi (POD modes)
        num_modes  : Maximum number of POD modes to use
        Ux_dict    : Dictionary containing velocity snapshots, keyed by Reynolds number
        Re         : Reynolds number (used to extract the corresponding snapshot)

    """
    
    if not hasattr(pod_object,'phi_pod'):
        raise ValueError("POD not computed yet. run compute_pod_method_of_snapshots() at first")

    errors = []
    for n in range(1, num_modes + 1):
        phi_n = pod_object.phi_pod[:, :n]
        reconstruction = phi_n @ (phi_n.T @ Ux_dict[Re])
        error = np.linalg.norm(Ux_dict[Re] - reconstruction)
        errors.append(error)

    # Plot
    plt.figure(figsize=(8, 5))
    plt.plot(range(1, num_modes + 1), errors, marker='o', color=sns.color_palette("viridis", n_colors=1)[0])
    plt.xlabel('Number of POD Modes', fontsize=12)
    plt.ylabel('Reconstruction Error (Frobenius norm)', fontsize=12)
    plt.title(f'Re = {Re} — Ux Reconstruction Error', fontsize=14)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()


def plot_AllCoff_once(modes, snapshots, angles,
                                 n_show=10, cmap_name='afmhot',
                                 save_path=None, Re=None):
    
    
     coeffs = modes.T @ snapshots
    
     # -- pick colours from the sequential cmap --
     n_modes = min(n_show, coeffs.shape[0])
     cmap = plt.get_cmap(cmap_name)
     colors = cmap(np.linspace(0, 0.7, n_modes))
    
     plt.figure(figsize=(12, 8))
     for i in range(n_modes):
         plt.plot(angles, coeffs[i, :],
                  marker='o', linestyle='-',
                  color=colors[i],
                  label=f'Mode {i+1}')
    
     # --- axes & styling ---
     ax = plt.gca()
     for spine in ax.spines.values():
         spine.set_linewidth(2)
    
     ax.tick_params(axis='both', which='major',
                    labelsize=12, width=2, length=6)
     ax.minorticks_on()
     ax.tick_params(axis='both', which='minor', length=4)
    
     plt.xlabel('Angle (degrees)', fontsize=16)
     plt.ylabel('Mode Coefficient', fontsize=16)
     plt.legend()
     plt.grid(True)
     plt.tight_layout()
     plt.savefig(save_path, bbox_inches="tight")
 
     plt.show()
    
     return coeffs
    
