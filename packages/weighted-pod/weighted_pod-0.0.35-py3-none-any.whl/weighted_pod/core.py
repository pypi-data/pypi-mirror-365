#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 24 13:55:26 2025

@author: hakan

Core WeightedPOD implementation for CFD analysis with non-uniform mesh.

This module contains the main WeightedPOD class for computing POD modes
with volume-weighted inner products.
"""

import numpy as np 
import matplotlib.pyplot as plt
from scipy.linalg import svd, eigh 
import gc  # For memory management



class WeightedPOD:
    """
        Parameters:
        -----------
        data_matrix : numpy.ndarray
            Shape (N, M) where N is spatial points and M is number of snapshots
        volumes : numpy.ndarray
            Shape (N,) containing cell volumes for each spatial point
        mean_subtraction : bool
            Whether to subtract temporal mean (default: True)

       Attributes:
       -----------
        X : numpy.ndarray
          Input data matrix
        volumes : numpy.ndarray
          Cell volumes for weighting
        N : int
          Number of spatial points
        M : int
          Number of snapshots
        phi_pod : numpy.ndarray
            Spatial POD modes
        a_pod : numpy.ndarray
            Temporal coefficients
        lambda_pod : numpy.ndarray
            Eigenvalues (energy content)
        energy_content : numpy.ndarray
            Energy percentage of each mode
        cumulative_energy : numpy.ndarray
            Cumulative energy percentage
            
    """
    
    def __init__(self, data_matrix, volumes, mean_subtraction=True):
        # you have to convert to float32 to save memory 
        self.X = data_matrix.astype(np.float32)
        self.volumes = volumes.astype(np.float32)
        self.mean_subtraction = mean_subtraction
        self.N, self.M = self.X.shape  # N = spatial points, M = snapshots
        
        print(f"Initializing POD with {self.N:,} spatial points and {self.M} snapshots")
      #  print(f"Data memory usage: ~{(self.X.nbytes / 1e9):.2f} GB")
      #  print(f"Volume memory usage: ~{(self.volumes.nbytes / 1e6):.1f} MB")  
        
        # Subtract mean if requested
        if self.mean_subtraction:
            print("Computing and subtracting mean...")
            self.X_mean = np.mean(self.X, axis=1, keepdims=True)
            self.X_centered = self.X - self.X_mean
        else:
            self.X_mean = np.zeros((self.N, 1), dtype=np.float32)
            self.X_centered = self.X.copy()

    def compute_pod_method_of_snapshots(self):
        print(f"\nComputing POD using method of snapshots...")
        print(f"Data shape: {self.X.shape}")
        print(f"Volume weights shape: {self.volumes.shape}")
        
        sqrt_volumes = np.sqrt(self.volumes)
        
        # Apply weights element-wise (no large matrix creation)
        
        # X_centered (N,M) , sqrt_volumes(N,1) , X_weighted (N,M)
        X_weighted = self.X_centered * sqrt_volumes[:, np.newaxis]
        # Correlation Matrix , C = X.T @ W @ X -- for snapshot method  
        C = X_weighted.T @ X_weighted  # Shape: (M, M) 

        # Clean up weighted matrix to save memory
        del X_weighted
        gc.collect()

        # Eigendecomposition of square matrix (M,M)
        eigenvals, eigenvecs = eigh(C)
        # Sort in descending order
        idx = np.argsort(eigenvals)[::-1]
        eigenvals = eigenvals[idx]
        eigenvecs = eigenvecs[:, idx]
        
        # Filter out numerical zeros
     #   positive_mask = eigenvals > 1e-12
     #   eigenvals = eigenvals[positive_mask]
    #    eigenvecs = eigenvecs[:, positive_mask]
        n_modes = len(eigenvals)
                
        # Compute spatial POD modes
        print("Computing spatial POD modes and coefficients...")

        self.lambda_pod = eigenvals
        self.phi_pod = np.zeros((self.N, n_modes), dtype=np.float32)
        # build_coeffs = eigenvecs @ np.diag(eigenvals ** -0.5)
        #    self.phi_pod = self.X_centered @ build_coeffs  # Shape: (N, n_modes)
        for i in range(n_modes):
            # modes = X_centered @ eigenvectors / sqrt(eigenvalue) (this is the standard approach)
            # reference:  Modal Analysis of Fluid Flows: An Overview
            # Compute spatial mode
            self.phi_pod[:, i] = self.X_centered @ eigenvecs[:, i] / np.sqrt(eigenvals[i])  
        
    
        print("Verifying mode orthonormality:")
        for i in range(min(3, n_modes)):
            weighted_norm_squared = np.sum(self.volumes * self.phi_pod[:, i]**2)
            print(f"    Mode {i+1} weighted norm²: {weighted_norm_squared:.6f}")
            
        # Compute temporal coefficients using weighted inner product
        print("Computing temporal coefficients...")
        # vectorized  
        # A = phi^T @ diag(volumes) @ X_centered
        self.a_pod = np.diag(eigenvals ** 0.5) @ eigenvecs.conj().T

        # Energy content analysis
        total_energy = np.sum(eigenvals)
        self.energy_content = eigenvals / total_energy * 100
        self.cumulative_energy = np.cumsum(self.energy_content)
        
        print("\nPOD computation completed successfully!")
        print(f"First mode captures {self.energy_content[0]:.2f}% of total energy")
        print(f"First 3 modes capture {self.cumulative_energy[2]:.2f}% of total energy")
        
        return self.phi_pod, self.a_pod, self.lambda_pod

    def compute_pod_svd(self):
        """
        Compute POD using SVD approach.
        
        Returns:
        --------
        tuple
            (phi_pod_svd, a_pod_svd, lambda_pod_svd) - spatial modes, temporal coefficients, eigenvalues
        """

        print("Computing POD using SVD approach...")
        # Apply weights element-wise
        sqrt_volumes = np.sqrt(self.volumes)
        X_weighted = self.X_centered * sqrt_volumes[:, np.newaxis]
        # SVD decomposition
        print("Performing SVD...")
        U, sigma, VT = svd(X_weighted, full_matrices=False)
        
                
        # Remove weight scaling element-wise
        self.phi_pod_svd = U / sqrt_volumes[:, np.newaxis]      
        self.a_pod_svd = sigma[:, np.newaxis] * VT
        self.lambda_pod_svd = sigma**2
        
        total_energy_svd = np.sum(self.lambda_pod_svd)
        self.energy_content_svd = self.lambda_pod_svd / total_energy_svd * 100      
        self.cumulative_energy_svd = np.cumsum(self.energy_content_svd)
    
        
        
        # Clean up
        del X_weighted
        gc.collect()
        
        return self.phi_pod_svd, self.a_pod_svd, self.lambda_pod_svd
    
    
    def reconstruct_field(self, n_modes, snapshot_idx=None, method='snapshots'):
        """
        Reconstruct flow field using first n_modes.
        
        Parameters:
        -----------
        n_modes : int
            Number of modes to use for reconstruction
        snapshot_idx : int, optional
            Index of specific snapshot to reconstruct. If None, reconstructs all.
        method : str, optional
            POD method used ('snapshots' or 'svd'). Default is 'snapshots'.
            
        Returns:
        --------
        numpy.ndarray
            Reconstructed field(s)
        """
    

        if method == 'snapshots':
            if not hasattr(self, 'phi_pod') or not hasattr(self, 'a_pod'):
                raise ValueError("POD not computed yet with method of snapshots. Run compute_pod_method_of_snapshots() first.")
            phi = self.phi_pod
            a = self.a_pod
        elif method == 'svd':
            if not hasattr(self, 'phi_pod_svd') or not hasattr(self, 'a_pod_svd'):
                raise ValueError("POD not computed yet with SVD method. Run compute_pod_svd() first.")
            phi = self.phi_pod_svd
            a = self.a_pod_svd
        else:
            raise ValueError("Invalid method. Use 'snapshots' or 'svd'.")
    
        n_modes = min(n_modes, phi.shape[1])
    
        if snapshot_idx is not None:
            # Reconstruct single snapshot
            reconstructed = self.X_mean.flatten() + \
                np.sum([a[i, snapshot_idx] * phi[:, i] for i in range(n_modes)], axis=0)
            print(f"reconstructed shape is {reconstructed.shape}")
            return reconstructed
        else:
            # Reconstruct all snapshots
            reconstructed = self.X_mean + phi[:, :n_modes] @ a[:n_modes, :]
            print(f"reconstructed shape is {reconstructed.shape}")
            return reconstructed
