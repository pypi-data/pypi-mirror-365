# Overview
This is a package to ADD realistic sources of noise to electrical load profiles. 
This is useful for testing the robustness of algorithms to noise, to enhance the realism of synthetic data, or to generate augmented data for machine learning purposes.

The overal approach is as follows:
- The package contains various `Perturbations`, such as perturbations to add Gaussian or Ornstein-Uhlenbeck noise, or to simulate measurement deadbands (and many others)
- You decide which perturbations you want to use, and you add them to a `Pipeline` object.
- You can call `pipeline.apply(profiles)`, and the pipeline sequentially applies the various perturbations to the given profiles.

Note, the package expects `profiles` as a 2D array (timesteps X measurement devices)

## Examples
On our [Github](https://github.com/Flinverdaasdonk/noisy_load_profiles) We have examples that demonstrate basic usage, advanced usage, and how to construct new Perturbations.

Below we show the most barebones example of a pipeline applying two types of noise.

```
from noisy_load_profiles import Pipeline, perturbations
import numpy as np


# initialize some profiles
timesteps = 10
n_profiles = 2
profiles = np.ones((timesteps, n_profiles)) # 2 profiles with 10 timesteps each; example


# Initialize some pertubations
gaussian_noise = perturbations.MultiplicativeGaussianNoise(mean=0.0, std=0.01, seed=42)
deadband = perturbations.PercentualDeadBand(seed=42)

# construct the pipeline
pipeline = Pipeline([gaussian_noise, deadband])


# apply the perturbation to the profiles
perturbed_profiles = pipeline.apply(profiles)

```