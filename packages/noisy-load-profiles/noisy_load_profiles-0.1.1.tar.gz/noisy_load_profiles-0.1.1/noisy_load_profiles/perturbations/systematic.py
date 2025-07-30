import numpy as np
from typing import Dict, Any, Optional
from ..base import Perturbation


class ConstantRandomPercentualBias(Perturbation):
    """
    Applies multiplicative Gaussian noise to load profiles.
    
    The perturbation multiplies each profile by (1 + noise) where noise is
    sampled from a Gaussian distribution with specified mean and standard deviation.
    
    Formula: perturbed_profile = profile * (1 + gaussian_noise)
    """
    
    def __init__(self, uniform_low: float = -1, uniform_high: float = 1,
                 seed: Optional[int] = None, transformation: Optional[Dict[str, Any]] = None, 
                 track_input_profiles: bool = False):
        """
        Initialize the MultiplicativeGaussianNoise perturbation.
        
        Parameters:
        -----------
        uniform_low : float, default=-1
            Lower bound of the uniform distribution for bias
        uniform_high : float, default=1
            Upper bound of the uniform distribution for bias
        seed : int, optional
            Random seed for reproducibility
        transformation : Dict[str, Any], optional
            Pre-computed transformation parameters containing 'noise_samples'
        """
        super().__init__(seed=seed, transformation=transformation, track_input_profiles=track_input_profiles)
        
        self.uniform_low = uniform_low
        self.uniform_high = uniform_high
        
        # Store configuration
        self._config = {
            'uniform_low': uniform_low,
            'uniform_high': uniform_high
        }
        
        # Validate parameters
        if uniform_low >= uniform_high:
            raise ValueError(f"uniform_low ({uniform_low}) must be less than uniform_high ({uniform_high})")
    
    def _infer_transformation(self, profiles: np.ndarray) -> Dict[str, Any]:
        """
        Generate noise samples with the same shape as the input profiles.
        
        Parameters:
        -----------
        profiles : np.ndarray
            2D array where each column is a load profile, each row is a timestep
        """
        # Generate noise samples with same shape as profiles
        n_columns = profiles.shape[1]
        base_biases = np.random.uniform(low=self.uniform_low, high=self.uniform_high, size=(1, n_columns))

        abs_profiles = np.abs(profiles)
        # get the mean per column
        mean_profiles = np.mean(abs_profiles, axis=0, keepdims=True)
        # calculate the bias as a percentage of the mean
        biases = base_biases * mean_profiles 
        
        
        transformation = {
            'biases': biases,
            'shape': biases.shape,
            'uniform_low': self.uniform_low,
            'uniform_high': self.uniform_high}

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
        
        # Add the biases to the profiles
        biases = self._transformation['biases']
        perturbed_profiles = profiles + biases

        
        return perturbed_profiles
    




class ConstantRandomPercentualScaling(Perturbation):
    """
    Applies multiplicative Gaussian noise to load profiles.
    
    The perturbation multiplies each profile by (1 + noise) where noise is
    sampled from a Gaussian distribution with specified mean and standard deviation.
    
    Formula: perturbed_profile = profile * (1 + gaussian_noise)
    """
    
    def __init__(self, uniform_low: float = 0.8, uniform_high: float = 1.2,
                 seed: Optional[int] = None, transformation: Optional[Dict[str, Any]] = None,
                 track_input_profiles: bool = False):
        """
        Initialize the MultiplicativeGaussianNoise perturbation.
        
        Parameters:
        -----------
        uniform_low : float, default=-1
            Lower bound of the uniform distribution for bias
        uniform_high : float, default=1
            Upper bound of the uniform distribution for bias
        seed : int, optional
            Random seed for reproducibility
        transformation : Dict[str, Any], optional
            Pre-computed transformation parameters containing 'noise_samples'
        """
        super().__init__(seed=seed, transformation=transformation, track_input_profiles=track_input_profiles)
        
        self.uniform_low = uniform_low
        self.uniform_high = uniform_high
        
        # Store configuration
        self._config = {
            'uniform_low': uniform_low,
            'uniform_high': uniform_high
        }
        
        # Validate parameters
        if uniform_low >= uniform_high:
            raise ValueError(f"uniform_low ({uniform_low}) must be less than uniform_high ({uniform_high})")
    
    def _infer_transformation(self, profiles: np.ndarray) -> Dict[str, Any]:
        """
        Generate noise samples with the same shape as the input profiles.
        
        Parameters:
        -----------
        profiles : np.ndarray
            2D array where each column is a load profile, each row is a timestep
        """
        # Generate noise samples with same shape as profiles
        n_columns = profiles.shape[1]
        base_scaling = np.random.uniform(low=self.uniform_low, high=self.uniform_high, size=(1, n_columns))
        
        transformation = {
            'scaling': base_scaling,
            'shape': base_scaling.shape,
            'uniform_low': self.uniform_low,
            'uniform_high': self.uniform_high}

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

        # Add the biases to the profiles
        scaling = self._transformation['scaling']

        perturbed_profiles = profiles * scaling

        
        return perturbed_profiles
    

class DiscreteTimeShift(Perturbation):
    """
    For each column, randomly shift values forward or backward by a random amount.
    The shift amount is uniformly sampled between shift_amount_lower_limit and shift_amount_upper_limit.
    The shift is applied with a given probability (shift_chance).
    If shifted, the values that were shifted away from are replaced with the closest known value.
    E.g. if we have [a, b, c, d, e, f, g] and we shift it with -2, we get [c, d, e, f, g, ?, ?], 
    and the question marks are replaced with the last value of the column, resulting in [c, d, e, f, g, g, g] 

    Stored transformation
    ---------------------
    {
        "do_shift": np.ndarray bool (C,),
        "shift_amounts": np.ndarray int (C,),
    }
    """

    def __init__(self, shift_chance: float, shift_amount_lower_limit: int, shift_amount_upper_limit: int, seed: Optional[int] = None, transformation: Optional[Dict[str, Any]] = None, track_input_profiles: bool = False):
        super().__init__(seed=seed, transformation=transformation, track_input_profiles=track_input_profiles)

        self.shift_chance = shift_chance
        if not (0.0 <= self.shift_chance <= 1.0):
            raise ValueError("shift_chance must be in [0, 1]")

        self.shift_amount_lower_limit = shift_amount_lower_limit
        self.shift_amount_upper_limit = shift_amount_upper_limit

        if not isinstance(self.shift_amount_lower_limit, int) or not isinstance(self.shift_amount_upper_limit, int):
            raise TypeError(f"shift_amount_lower_limit and shift_amount_upper_limit must be integers, {shift_amount_lower_limit} and {shift_amount_upper_limit} provided")

        if self.shift_amount_lower_limit > self.shift_amount_upper_limit:
            raise ValueError(f"shift_amount_lower_limit ({shift_amount_lower_limit}) must be less than or equal to shift_amount_upper_limit ({shift_amount_upper_limit})")

        self._config = {shift_chance: self.shift_chance,
                        'shift_amount_lower_limit': self.shift_amount_lower_limit,
                        'shift_amount_upper_limit': self.shift_amount_upper_limit}


    def _infer_transformation(self, profiles: np.ndarray) -> Dict[str, Any]:

        t_steps, n_cols = profiles.shape

        # uniform random sampling between 0 and 1 to assess shift chance
        do_shift = np.random.uniform(0, 1, size=n_cols) <= self.shift_chance

        shift_amounts = np.random.randint(self.shift_amount_lower_limit, self.shift_amount_upper_limit + 1, size=n_cols)

        # mask shift_amounts with do_shift
        shift_amounts[~do_shift] = 0

        transformation = {
            "do_shift": do_shift,
            "shift_amounts": shift_amounts,
        }
        return transformation

    def _apply_perturbation(self, profiles: np.ndarray) -> np.ndarray:

        t_steps, n_cols = profiles.shape
        do_shift = self._transformation["do_shift"]
        shift_amounts = self._transformation["shift_amounts"]

        new_profiles = profiles.copy()

        for col in range(n_cols):
            if do_shift[col]:
                shift_amount = shift_amounts[col]
                if shift_amount == 0:
                    # nothing to do
                    continue

                # roll the column values
                new_profiles[:, col] = np.roll(profiles[:, col], shift=shift_amount)

                if shift_amount > 0:
                    # if shift is positive, set the first `shift_amount` values the first value of the column
                    new_profiles[:shift_amount, col] = new_profiles[shift_amount, col] 

                else:
                    # if shift is negative, set the last `shift_amount` values to the last value of the column
                    new_profiles[shift_amount:, col] = new_profiles[shift_amount, col]

                
        return new_profiles