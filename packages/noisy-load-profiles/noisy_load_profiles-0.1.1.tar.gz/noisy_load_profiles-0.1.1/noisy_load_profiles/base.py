import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union
import copy

class Perturbation(ABC):
    """
    Base class for all perturbations that can be applied to load profiles.
    
    Each perturbation should:
    1. Store initialization parameters
    2. Infer transformation from input profiles
    3. Apply the perturbation using the inferred transformation
    """
    
    def __init__(self, seed: Optional[int] = None, transformation: Optional[Dict[str, Any]] = None, track_input_profiles: bool = False):
        """
        Initialize the perturbation.
        
        Parameters:
        -----------
        seed : int, optional
            Random seed for reproducibility
        transformation : Dict[str, Any], optional
            Pre-computed transformation parameters. If provided, this transformation
            will be used instead of inferring from data.
        """
        self.seed = seed
        self._config = {}
        self._transformation = transformation
        self._is_applied = False
        self.track_input_profiles = track_input_profiles
        
        # Set random seed if provided
        if seed is not None:
            np.random.seed(seed)
    
    @abstractmethod
    def _infer_transformation(self, profiles: np.ndarray) -> Dict[str, Any]:
        """
        Infer and store the transformation parameters from the input profiles.
        
        This method should analyze the profiles and set self._transformation
        with the appropriate transformation parameters (noise values, bias values, shape, etc.)
        
        Parameters:
        -----------
        profiles : np.ndarray
            2D array where each column is a load profile, each row is a timestep

        Returns:
        transformation : np.ndarray
            The transformation parameters inferred from the profiles.
        """
        pass

    def set_transformation(self, transformation: np.ndarray) -> None:
        self._transformation = transformation
        return
    

    def get_transformation(self) -> Optional[Dict[str, Any]]:
        """
        Get the transformation parameters that were inferred/applied.
        
        Returns:
        --------
        Dict[str, Any] or None
            Dictionary containing transformation parameters, or None if not applied yet
        """
        if not self._is_applied:
            return None
        return copy.deepcopy(self._transformation)

    
    @abstractmethod
    def _apply_perturbation(self, profiles: np.ndarray) -> np.ndarray:
        """
        Apply the perturbation using the stored transformation parameters.
        
        This method should use self._transformation to modify the profiles.
        
        Parameters:
        -----------
        profiles : np.ndarray
            2D array where each column is a load profile, each row is a timestep
            
        Returns:
        --------
        np.ndarray
            The perturbed profiles with same shape as input
        """
        pass
    
    def apply(self, profiles: np.ndarray) -> np.ndarray:
        """
        Apply the perturbation to the input profiles.
        
        Parameters:
        -----------
        profiles : np.ndarray
            2D array where each column is a load profile, each row is a timestep
            
        Returns:
        --------
        np.ndarray
            Perturbed profiles with same shape as input
        """
        # Validate input
        self._validate_input(profiles)

        self.set_seed(self.seed)  # Ensure seed is set for reproducibility
        
        # Only infer transformation if we don't already have one
        if self._transformation is None:
            transformation = self._infer_transformation(profiles)
            self.set_transformation(transformation)

        if self.track_input_profiles:
            self.input_profiles = profiles
        
        # Apply the perturbation using the transformation (inferred or provided)
        perturbed_profiles = self._apply_perturbation(profiles)
        
        # Mark as applied
        self._is_applied = True
        
        return perturbed_profiles
    
    def _validate_input(self, profiles: np.ndarray) -> None:
        """Validate that the input profiles are in the expected format."""
        if not isinstance(profiles, np.ndarray):
            raise TypeError("Profiles must be a numpy array")
        
        if profiles.ndim != 2:
            raise ValueError("Profiles must be a 2D array (timesteps x profiles)")
        
        if profiles.size == 0:
            raise ValueError("Profiles array cannot be empty")
    
    @property
    def config(self) -> Dict[str, Any]:
        """
        Get the configuration parameters used to initialize this perturbation.
        
        Returns:
        --------
        Dict[str, Any]
            Dictionary containing initialization parameters
        """
        config = copy.deepcopy(self._config)
        config['seed'] = self.seed
        config['perturbation_type'] = self.__class__.__name__
        return config
    
    
    def reset(self) -> None:
        """Reset the perturbation state, clearing transformation parameters."""
        self._transformation = None
        self._is_applied = False
        
        # Re-set seed if it was provided
        self.set_seed(self.seed)
    
    def set_seed(self, seed: int) -> None:
        """
        Set or change the random seed.
        
        Parameters:
        -----------
        seed : int
            New random seed
        """
        if self.seed is None:
            return

        self.seed = seed
        np.random.seed(seed)
    
    def __repr__(self) -> str:
        """String representation of the perturbation."""
        config_str = ", ".join([f"{k}={v}" for k, v in self._config.items()])
        return f"{self.__class__.__name__}({config_str})"
