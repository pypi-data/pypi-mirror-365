import numpy as np
from typing import Dict, Any, Optional, List
from ..base import Perturbation
import copy

class MultiplicativeGaussianNoise(Perturbation):
    """
    Applies multiplicative Gaussian noise to load profiles.
    
    The perturbation multiplies each profile by (1 + noise) where noise is
    sampled from a Gaussian distribution with specified mean and standard deviation.
    
    Formula: perturbed_profile = profile * (1 + gaussian_noise)
    """
    
    def __init__(self, mean: float = 0.0, std: float = 0.01, 
                 seed: Optional[int] = None, transformation: Optional[Dict[str, Any]] = None,
                 track_input_profiles: bool = False):
        """
        Initialize the MultiplicativeGaussianNoise perturbation.
        
        Parameters:
        -----------
        mean : float, default=0.0
            Mean of the Gaussian noise distribution
        std : float, default=0.01
            Standard deviation of the Gaussian noise distribution
        seed : int, optional
            Random seed for reproducibility
        transformation : Dict[str, Any], optional
            Pre-computed transformation parameters containing 'noise_samples'
        """
        super().__init__(seed=seed, transformation=transformation, track_input_profiles=track_input_profiles)
        
        self.mean = mean
        self.std = std
        
        # Store configuration
        self._config = {
            'mean': mean,
            'std': std
        }
        
        # Validate parameters
        if std < 0:
            raise ValueError("Standard deviation must be non-negative")
    
    def _infer_transformation(self, profiles: np.ndarray) -> Dict[str, Any]:
        """
        Generate noise samples with the same shape as the input profiles.
        
        Parameters:
        -----------
        profiles : np.ndarray
            2D array where each column is a load profile, each row is a timestep
        """
        # Generate noise samples with same shape as profiles
        noise_samples = np.random.normal(loc=self.mean, scale=self.std, size=profiles.shape)
        
        transformation = {
            'noise_samples': noise_samples,
            'mean': self.mean,
            'std': self.std,
            'shape': profiles.shape
        }
        return transformation
    

    def _apply_perturbation(self, profiles: np.ndarray) -> np.ndarray:
        """
        Apply multiplicative Gaussian noise using stored transformation parameters.
        
        Parameters:
        -----------
        profiles : np.ndarray
            2D array where each column is a load profile, each row is a timestep
            
        Returns:
        --------
        np.ndarray
            The perturbed profiles: profiles * (1 + noise_samples)
        """

        # Verify shape compatibility
        expected_shape = self._transformation['shape']
        if profiles.shape != expected_shape:
            raise ValueError(f"Profile shape {profiles.shape} doesn't match expected shape {expected_shape}")
        
        # Apply multiplicative noise: profiles * (1 + noise)
        noise_samples = self._transformation['noise_samples']
        perturbed_profiles = profiles * (1 + noise_samples)
        
        return perturbed_profiles
    





class AdditiveOUNoise(Perturbation):
    """
    Adds additive Ornstein–Uhlenbeck (OU) noise to each column.
    Put simply, OU noise is like a random walk that has a tendency to revert to a mean value (mu) over time.

    Discrete update (Euler–Maruyama):
        x[t+1] = x[t] + theta * (mu - x[t]) * dt + sigma_eff[c] * sqrt(dt) * N(0,1)

    Simplified scaling:
        sigma_eff[c] = sigma * mean(abs(profiles[:, c]))
    where `sigma` is a dimensionless fraction of the column's mean absolute magnitude.
    """

    def __init__(
        self,
        theta: float = 0.5,
        mu: float = 0.0,
        sigma: float = 0.05,          # fraction of mean(|column|)
        dt: float = 1.0,
        per_column_independent: bool = True,
        eps_scale: float = 1e-12,
        seed: Optional[int] = None,
        transformation: Optional[Dict[str, Any]] = None,
        track_input_profiles: bool = False,
    ):
        super().__init__(seed=seed, transformation=transformation, track_input_profiles=track_input_profiles)

        if theta <= 0:
            raise ValueError("theta must be > 0")
        if dt <= 0:
            raise ValueError("dt must be > 0")
        if sigma < 0:
            raise ValueError("sigma must be >= 0")
        if eps_scale <= 0:
            raise ValueError("eps_scale must be > 0")

        self.theta = float(theta)
        self.mu = float(mu)
        self.sigma = float(sigma)
        self.dt = float(dt)
        self.per_column_independent = per_column_independent
        self.eps_scale = float(eps_scale)

        self._config = {
            "theta": self.theta,
            "mu": self.mu,
            "sigma": self.sigma,
            "dt": self.dt,
            "per_column_independent": self.per_column_independent,
            "eps_scale": self.eps_scale,
        }

    # -------- required abstract-method implementations --------

    def _infer_transformation(self, profiles: np.ndarray) -> Dict[str, Any]:
        t_steps, n_cols = profiles.shape

        # per-column scaling based on mean absolute magnitude
        mean_abs = np.mean(np.abs(profiles), axis=0)
        mean_abs = np.maximum(mean_abs, self.eps_scale)
        sigma_eff = self.sigma * mean_abs


        noise = self._simulate_ou(
            t_steps=t_steps,
            n_cols=n_cols,
            theta=self.theta,
            mu=self.mu,
            sigma_eff=sigma_eff,
            dt=self.dt,
            per_column_independent=self.per_column_independent,
        )

        summary = {
            "noise_std_per_col": noise.std(axis=0, ddof=1).tolist() if t_steps > 1 else [0.0] * n_cols,
            "noise_mean_per_col": noise.mean(axis=0).tolist(),
            "mean_abs_per_col": mean_abs.tolist(),
        }

        transformation = {
            "noise": noise,
            "theta": self.theta,
            "mu": self.mu,
            "dt": self.dt,
            "sigma": self.sigma,
            "sigma_eff": sigma_eff,
            "shape": (t_steps, n_cols),
            "per_column_independent": self.per_column_independent,
            "summary": summary,
        }
        return transformation

    def _apply_perturbation(self, profiles: np.ndarray) -> np.ndarray:
        noise = self._transformation["noise"]
        if noise.shape != profiles.shape:
            raise ValueError(f"Stored noise shape {noise.shape} does not match profiles shape {profiles.shape}")
        return profiles + noise

    # -------- helpers --------

    @staticmethod
    def _simulate_ou(
        t_steps: int,
        n_cols: int,
        theta: float,
        mu: float,
        sigma_eff: np.ndarray,
        dt: float,
        per_column_independent: bool,
    ) -> np.ndarray:

        x0 = np.zeros(n_cols, dtype=float)  # initial state

        out = np.empty((t_steps, n_cols), dtype=float)
        out[0, :] = x0
        sqrt_dt = np.sqrt(dt)

        if per_column_independent:
            for t in range(1, t_steps):
                z = np.random.normal(size=n_cols)
                out[t, :] = (
                    out[t - 1, :]
                    + theta * (mu - out[t - 1, :]) * dt
                    + sigma_eff * sqrt_dt * z
                )
        else:
            for t in range(1, t_steps):
                z_shared = np.random.normal()
                out[t, :] = (
                    out[t - 1, :]
                    + theta * (mu - out[t - 1, :]) * dt
                    + sigma_eff * sqrt_dt * z_shared
                )
        return out