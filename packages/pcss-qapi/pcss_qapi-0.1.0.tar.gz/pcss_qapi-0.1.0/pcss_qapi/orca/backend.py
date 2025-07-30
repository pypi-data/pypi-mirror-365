"""Convenience backend for orca"""
from typing import Literal, Any
from collections.abc import Callable
import warnings

import numpy as np
import numpy.typing as npt

from torch import nn

from pcss_qapi.utils.exceptions import MissingOptionalDependencyError
try:
    from ptseries.tbi.tbi_abstract import TBIDevice
    from ptseries.tbi.tbi_single_loop import TBISingleLoop
    from ptseries.tbi.tbi_multi_loop import TBIMultiLoop
    from ptseries.tbi.fixed_random_unitary import FixedRandomUnitary
    from ptseries.tbi import create_tbi
    from ptseries.algorithms.binary_solvers import BinaryBosonicSolver

    from pcss_qapi.orca.ptseries_integration import PTAdapter, ORCALayer, BBS_Adapter  # pylint: disable=ungrouped-imports
    from pcss_qapi.base.connection_base import ApiConnection
except ImportError as ie:
    PACKAGE = str(ie.name)
    if 'ptseries' in PACKAGE:
        PACKAGE = 'ptseries (privately distributed - https://sdk.orcacomputing.com/)'
    raise MissingOptionalDependencyError(package_name=PACKAGE) from ie


class OrcaBackend:
    """Convenience class that provides different ptseries classes that use pcss_qapi"""

    _tbi_map = {
        'single_loop_simulator': 'single-loop',
        'multi_loop_simulator': 'multi-loop'
    }

    def __init__(self, connection: ApiConnection, name: str) -> None:
        self._connection = connection
        self.name = name

    def get_tbi(
        self,
        n_loops: int = 1,
        loop_lengths: list[int] | tuple[int, ...] | npt.NDArray[np.int_] | None = None,
        postselected: bool | None = None,
        postselection: bool = True,
        postselection_threshold: int | None = None,
        simulator_params: dict | None = None
    ) -> TBIDevice | TBISingleLoop | TBIMultiLoop | FixedRandomUnitary:
        """Get a PT instance connected to the api"""
        if self.name in OrcaBackend._tbi_map:
            if simulator_params is None:
                simulator_params = {}
            return create_tbi(
                OrcaBackend._tbi_map.get(self.name, None),
                n_loops,
                loop_lengths,
                postselected,
                postselection,
                postselection_threshold,
                **simulator_params
            )
        return PTAdapter(
            self._connection,
            n_loops,
            loop_lengths,
            postselected,
            postselection,
            postselection_threshold,
            machine=self.name
        )

    def get_ptlayer(
        self,
        input_state: list[int] | tuple[int, ...] | npt.NDArray[np.int_] | None = None,
        in_features: str | int = "default",
        observable: Literal['avg-photons', 'covariances', 'correlations'] = "avg-photons",
        gradient_mode: Literal['parameter-shift', 'finite-difference', 'spsa'] = 'parameter-shift',
        gradient_delta: float = np.pi / 10,
        n_samples: int = 100,
        tbi_params: dict | None = None,
        n_tiling: int = 1,
    ) -> nn.Module:
        """
        Get a PTLayer instance that communicates with the backend's assigned quantum computer.

        Args:
            input_state (list[int] | tuple[int, ...] | npt.NDArray[np.int_] | None, optional):
                Input state for the tbi. If None defaults to an alternating series of 0s and 1s. Defaults to None.
            in_features (str | int, optional):
                Number fo layer input features. Defaults to "default".
            observable (Literal[&#39;avg, optional):
                Method of conversion from measurements to a tensor. Defaults to "avg-photons".
            gradient_mode (Literal[&#39;parameter, optional):
                Method to compute the gradient. Defaults to 'parameter-shift'.
            gradient_delta (float, optional):
                Delta to use with the parameter shift rule or for the finite difference. Defaults to np.pi/10.
            n_samples (int, optional):
                Number of samples to draw. Defaults to 100.
            tbi_params (dict | None, optional):
                Dictionary of optional parameters to instantiate the TBI. Defaults to None.
            n_tiling (int, optional):
                Uses n_tiling instances of PT Series and concatenates the results.
                Input features are distributed between tiles, which each have different trainable params.
                Defaults to 1.

        Returns:
            nn.Module: The parametrized PTLayer instance.
        """
        if tbi_params is None:
            tbi_params = {}

        if 'tbi_type' in tbi_params:
            warnings.warn('"tbi_type" is assigned automatically, ignoring set value.')

        return ORCALayer(
            self._connection,
            input_state=input_state,
            in_features=in_features,
            observable=observable,
            gradient_mode=gradient_mode,
            gradient_delta=gradient_delta,
            n_samples=n_samples,
            n_tiling=n_tiling,
            tbi_params=(tbi_params | {'tbi_type': OrcaBackend._tbi_map.get(self.name, 'PT')}),
            machine=self.name
        )

    def get_bbs(
        self,
        pb_dim: int,
        objective: np.ndarray | Callable[..., Any],
        input_state: list | None = None,
        tbi_params: dict | None = None,
        n_samples: int = 100,
        gradient_mode: Literal['parameter-shift', 'finite-difference', 'spsa'] = 'parameter-shift',
        gradient_delta: float = np.pi / 6,
        spsa_params: dict | None = None,
        device: str = "cpu",
        sampling_factor: int = 2,
        entropy_penalty: float = 0.1,
    ) -> BinaryBosonicSolver:
        """
        Get a BinaryBosonicSolver instance connected to the api

        Args:
            pb_dim (int):
                Dimension of the binary problem.
            objective (np.ndarray | Callable[..., Any]):
                The function to minimize.
            input_state (list | None, optional):
                The input state for the underlying PTLayer. Defaults to None.
            tbi_params (dict | None, optional):
                Optional params for the tbi. Defaults to None.
            n_samples (int, optional):
                Number of samples used for calculating expectation values. Defaults to 100.
            gradient_mode (Literal, optional):
                Gradient algorithm to use. Defaults to 'parameter-shift'.
            gradient_delta (float, optional):
                Delta value for parameter shift of finite difference algorithms. Defaults to np.pi/6.
            spsa_params (dict | None, optional):
                Optional parameters for the SPSA gradient method. Defaults to None.
            device (str, optional):
                PTLayer device. Defaults to "cpu".
            sampling_factor (int, optional):
                Number of times quantum samples are passed through the classical flipping layer. Defaults to 2.
            entropy_penalty (float, optional):
                Defaults to 0.1.

        Returns:
            BinaryBosonicSolver: BinaryBosonicSolver instance
        """

        if tbi_params is None:
            tbi_params = {}

        if 'tbi_type' in tbi_params:
            warnings.warn('"tbi_type" is assigned automatically, ignoring set value.')

        return BBS_Adapter(
            connection=self._connection,
            pb_dim=pb_dim,
            objective=objective,
            input_state=input_state,
            tbi_params=tbi_params | (tbi_params if tbi_params is not None else {}) | {
                'tbi_type': OrcaBackend._tbi_map.get(self.name, 'PT')},
            n_samples=n_samples,
            gradient_mode=gradient_mode,
            gradient_delta=gradient_delta,
            spsa_params=spsa_params,
            device=device,
            sampling_factor=sampling_factor,
            entropy_penalty=entropy_penalty,
            machine=self.name
        )

    def __repr__(self) -> str:
        return f"OrcaBackend[{self.name}] on connection {self._connection}"
