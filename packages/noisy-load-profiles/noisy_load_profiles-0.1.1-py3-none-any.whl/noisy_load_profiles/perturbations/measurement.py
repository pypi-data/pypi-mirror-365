import numpy as np
from typing import Dict, Any, Optional, Tuple, List
from ..base import Perturbation
import copy

# random zero-

class ZeroMeasurements(Perturbation):
    """
    Put Simply, this sometimes sets a measurements to zero, simulating an outage or a measurement error.

    This is done using a 2-state Markov Model

    States:
        0 = normal
        1 = zero/outage

    Parameters
    ----------
    f_zero : float, optional
        Target long-run fraction of zeros, in (0, 1). Used to derive (alpha, beta)
        together with (k_max, tail_eps).
    k_max : int, optional
        "Likely maximum" run length. Together with tail_eps, sets beta via
        P(L > k_max) = tail_eps for geometric run length.
    tail_eps : float, default 0.1
        Overflow probability for the likely-maximum definition.


    alpha : float, optional
        P(enter zero state | currently normal). Must be in (0, 1).
        If not provided, it is derived from (f_zero, k_max, tail_eps).
    beta : float, optional
        P(exit zero state | currently zero). Must be in (0, 1).
        If not provided, it is derived from (f_zero, k_max, tail_eps).


    per_column_independent : bool, default True
        If True, each column gets its own independent Markov path (same alpha/beta).
        If False, a single path is generated and applied to all columns.
    seed : int, optional
        Random seed for reproducibility.
    transformation : dict, optional
        Precomputed transformation that contains a 'zero_mask' of shape (T, C).

    Stored transformation
    ---------------------
    {
        'zero_mask': np.ndarray bool (T, C),
        'alpha': float,
        'beta': float,
        'f_zero_implied': float,
        'run_stats': {
            'n_runs_per_column': List[int],
            'run_lengths_per_column': List[List[int]],
        },
        'shape': (T, C),
        'per_column_independent': bool
    }
    """

    def __init__(
        self,
        f_zero: Optional[float] = None,
        k_max: Optional[int] = None,
        tail_eps: float = 0.1,
        alpha: Optional[float] = None,
        beta: Optional[float] = None,
        per_column_independent: bool = True,
        seed: Optional[int] = None,
        transformation: Optional[Dict[str, Any]] = None,
        track_input_profiles: bool = False,
    ):
        super().__init__(seed=seed, transformation=transformation, track_input_profiles=track_input_profiles)

        # store configuration
        self.alpha = alpha
        self.beta = beta
        self.f_zero = f_zero
        self.k_max = k_max
        self.tail_eps = tail_eps
        self.per_column_independent = per_column_independent

        self._config = {
            "alpha": alpha,
            "beta": beta,
            "f_zero": f_zero,
            "k_max": k_max,
            "tail_eps": tail_eps,
            "per_column_independent": per_column_independent,
        }

        # basic validation of provided combos will be finalized in _infer_transformation
        if self.alpha is not None and not (0.0 < self.alpha < 1.0):
            raise ValueError("alpha must be in (0, 1)")
        if self.beta is not None and not (0.0 < self.beta < 1.0):
            raise ValueError("beta must be in (0, 1)")
        if self.f_zero is not None and not (0.0 < self.f_zero < 1.0):
            raise ValueError("f_zero must be in (0, 1)")
        if self.k_max is not None and self.k_max <= 0:
            raise ValueError("k_max must be a positive integer")
        if not (0.0 < self.tail_eps < 1.0):
            raise ValueError("tail_eps must be in (0, 1)")

    # -------- public helpers --------

    @staticmethod
    def pick_alpha_beta_from_targets(f_zero: float, k_max: int, tail_eps: float) -> Tuple[float, float]:
        """
        Compute (alpha, beta) from intuitive targets:

        - Choose beta so that P(L > k_max) = tail_eps for geometric run length:
              P(L > k) = (1 - beta)^k  =>  beta = 1 - tail_eps^(1/k_max)
        - Choose alpha to match long-run zero fraction:
              f_zero = alpha / (alpha + beta)  =>  alpha = f_zero * beta / (1 - f_zero)
        """
        if not (0.0 < f_zero < 1.0):
            raise ValueError("f_zero must be in (0, 1)")
        if k_max <= 0:
            raise ValueError("k_max must be positive")
        if not (0.0 < tail_eps < 1.0):
            raise ValueError("tail_eps must be in (0, 1)")

        beta = 1.0 - tail_eps ** (1.0 / k_max)
        alpha = f_zero * beta / (1.0 - f_zero)
        return alpha, beta

    # -------- core abstract-method implementations --------

    def _infer_transformation(self, profiles: np.ndarray) -> Dict[str, Any]:
        t_steps, n_cols = profiles.shape

        # finalize (alpha, beta)
        alpha, beta = self._resolve_alpha_beta()

        # generate zero mask(s)
        if self.per_column_independent:
            zero_mask = np.zeros((t_steps, n_cols), dtype=bool)
            for c in range(n_cols):
                zero_mask[:, c] = self._sample_markov_mask(t_steps, alpha, beta)
        else:
            mask = self._sample_markov_mask(t_steps, alpha, beta)
            zero_mask = np.repeat(mask[:, None], n_cols, axis=1)

        # collect run stats (useful for inspection/testing)
        run_stats = self._collect_run_stats(zero_mask)

        f_zero_implied = float(zero_mask.mean())

        transformation = {
            "zero_mask": zero_mask,
            "alpha": float(alpha),
            "beta": float(beta),
            "f_zero_implied": f_zero_implied,
            "run_stats": run_stats,
            "shape": zero_mask.shape,
            "per_column_independent": self.per_column_independent,
        }
        return transformation

    def _apply_perturbation(self, profiles: np.ndarray) -> np.ndarray:

        zero_mask = self._transformation["zero_mask"]
        if zero_mask.shape != profiles.shape:
            raise ValueError(
                f"Stored zero_mask shape {zero_mask.shape} does not match profiles shape {profiles.shape}"
            )

        perturbed = profiles.copy()
        perturbed[zero_mask] = 0.0
        return perturbed

    # -------- internal helpers --------

    def _resolve_alpha_beta(self) -> Tuple[float, float]:
        # priority 1: explicit alpha & beta
        if self.alpha is not None and self.beta is not None:
            return float(self.alpha), float(self.beta)

        # priority 2: derive from intuitive targets
        if self.f_zero is not None and self.k_max is not None:
            alpha, beta = self.pick_alpha_beta_from_targets(self.f_zero, self.k_max, self.tail_eps)
            return alpha, beta

        # otherwise insufficient information
        raise ValueError(
            "Insufficient parameters to determine (alpha, beta). "
            "Provide either both alpha and beta, or f_zero with k_max (and optional tail_eps)."
        )

    @staticmethod
    def _sample_markov_mask(t_steps: int, alpha: float, beta: float) -> np.ndarray:
        """
        Sample a boolean mask of length t_steps where True indicates zero/outage.
        """
        mask = np.zeros(t_steps, dtype=bool)
        state_zero = False
        for t in range(t_steps):
            if state_zero:
                # possibility to exit
                if np.random.random() < beta:
                    state_zero = False
            else:
                # possibility to enter
                if np.random.random() < alpha:
                    state_zero = True
            mask[t] = state_zero
        return mask

    @staticmethod
    def _collect_run_stats(zero_mask: np.ndarray) -> Dict[str, Any]:
        """
        Compute run statistics per column for diagnostics.
        """
        t_steps, n_cols = zero_mask.shape
        n_runs_per_column: List[int] = []
        run_lengths_per_column: List[List[int]] = []

        for c in range(n_cols):
            col = zero_mask[:, c]
            lengths = ZeroMeasurements._run_lengths(col)
            n_runs_per_column.append(len(lengths))
            run_lengths_per_column.append(lengths)

        return {
            "n_runs_per_column": n_runs_per_column,
            "run_lengths_per_column": run_lengths_per_column,
        }

    @staticmethod
    def _run_lengths(col_mask: np.ndarray) -> List[int]:
        """
        Return list of contiguous True run lengths.
        """
        if col_mask.size == 0:
            return []
        # identify starts and ends
        padded = np.concatenate(([False], col_mask, [False]))
        change = np.diff(padded.astype(int))
        starts = np.where(change == 1)[0]
        ends = np.where(change == -1)[0]
        lengths = (ends - starts).tolist()
        return lengths



class PercentualDeadBand(Perturbation):
    """
    Applies a deadband on percentage change relative to the last reported value.
    A deadband means that if the percentual change from the last reported value does NOT exceed the 'deadband threshold', you simply report the last reported value again.
    The deadband threshold decreases over time, allowing for more precise reporting as the process stabilizes.

    
    After each report, the acceptable percentual deviation shrinks over time as:

        deadband[t_since_report] = linspace(initial_deviation, 0.0, timesteps)[t]

    where t is capped at timesteps-1. When the percentual change exceeds the
    current threshold, the new value is reported and the schedule resets.

    Notes
    -----
    - t = 0 (first sample) always reports.
    - Percentual change is computed w.r.t. the last *reported* value:
          pct = abs(x_t - last_report) / max(abs(last_report), eps_den)
    - When the threshold reaches 0.0 (after `timesteps-1` steps), the next sample
      is always reported unless it is *exactly* equal to the last reported value.
    - Deterministic; no randomness involved.
    """

    def __init__(
        self,
        initial_deviation: float = 0.01,
        timesteps: int = 4,
        eps_den: float = 1e-12,
        seed: Optional[int] = None,
        transformation: Optional[Dict[str, Any]] = None,
        track_input_profiles: bool = False,
    ):
        super().__init__(seed=seed, transformation=transformation, track_input_profiles=track_input_profiles)

        if initial_deviation < 0.0:
            raise ValueError("initial_deviation must be >= 0")
        if timesteps <= 0:
            raise ValueError("timesteps must be a positive integer")
        if eps_den <= 0.0:
            raise ValueError("eps_den must be > 0")

        self.initial_deviation = float(initial_deviation)
        self.timesteps = int(timesteps)
        self.eps_den = float(eps_den)

        self._config = {
            "initial_deviation": self.initial_deviation,
            "timesteps": self.timesteps,
            "eps_den": self.eps_den,
        }

    # ------------- core abstract-method implementations -------------

    def _infer_transformation(self, profiles: np.ndarray) -> Dict[str, Any]:
        t_steps, n_cols = profiles.shape
        thresholds = np.linspace(self.initial_deviation, 0.0, self.timesteps)
        change_mask = np.zeros((t_steps, n_cols), dtype=bool)
        change_mask[0, :] = True  # first sample always reported

        # compute per-column change decisions
        for c in range(n_cols):
            last_report = profiles[0, c]
            t_since = 0
            for t in range(1, t_steps):
                # current threshold index (capped)
                idx = t_since if t_since < self.timesteps else self.timesteps - 1
                thr = thresholds[idx]                    

                denom = max(abs(last_report), self.eps_den)
                pct = abs(profiles[t, c] - last_report) / denom

                if pct > thr:
                    change_mask[t, c] = True
                    last_report = profiles[t, c]
                    t_since = 0
                else:
                    # keep previous report
                    change_mask[t, c] = False
                    t_since += 1

        # optional stats
        reports_per_column: List[int] = change_mask.sum(axis=0).tolist()

        transformation = {
            "change_mask": change_mask,
            "thresholds": thresholds,
            "shape": (t_steps, n_cols),
            "reports_per_column": reports_per_column,
            "initial_deviation": self.initial_deviation,
            "timesteps": self.timesteps,
            "eps_den": self.eps_den,
        }
        return transformation

    def _apply_perturbation(self, profiles: np.ndarray) -> np.ndarray:

        change_mask = self._transformation["change_mask"]
        if change_mask.shape != profiles.shape:
            raise ValueError(
                f"Stored change_mask shape {change_mask.shape} does not match profiles shape {profiles.shape}"
            )

        t_steps, n_cols = profiles.shape
        out = np.empty_like(profiles)

        # reconstruct reported series from change_mask
        for c in range(n_cols):
            last_val = profiles[0, c]
            out[0, c] = last_val
            for t in range(1, t_steps):
                if change_mask[t, c]:
                    last_val = profiles[t, c]
                out[t, c] = last_val

        return out



