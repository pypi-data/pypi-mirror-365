"""BinaryBosonicSolver adapter"""
from typing import Any
from collections.abc import Callable
import numpy as np
from ptseries.algorithms.binary_solvers import BinaryBosonicSolver
from pcss_qapi.orca.ptseries_integration.orca_layer import ORCALayer
from pcss_qapi.base.connection_base import ApiConnection


class BBS_Adapter(BinaryBosonicSolver):  # pylint:disable=invalid-name
    """BBS integrated with the api"""

    # pylint:disable=too-few-public-methods
    # pylint:disable=too-many-arguments
    # pylint:disable=too-many-positional-arguments
    # pylint:disable=R0801
    def __init__(
            self,
            connection: ApiConnection,
            pb_dim: int,
            objective: np.ndarray | Callable[..., Any],
            input_state: list | None = None,
            tbi_params: dict[str, Any] | None = None,
            n_samples: int = 100,
            gradient_mode: str = "parameter-shift",
            gradient_delta: float = np.pi / 6,
            spsa_params: dict | None = None,
            device: str = "cpu",
            sampling_factor: int = 2,
            entropy_penalty: float = 0.1,
            machine: str | None = None,
    ):

        super().__init__(
            pb_dim,
            objective,
            input_state,
            (tbi_params if tbi_params is not None else {}) | {'url': connection.task_endpoints_url},
            n_samples,
            gradient_mode,
            gradient_delta,
            spsa_params,
            device,
            sampling_factor,
            entropy_penalty,
        )

        self.pt_layer = ORCALayer(
            connection,
            input_state=self.input_state,
            in_features=0,
            observable=self.observable,
            gradient_mode=gradient_mode,
            gradient_delta=gradient_delta,
            n_samples=n_samples,
            n_tiling=self.n_tiling,
            tbi_params=tbi_params,
            machine=machine,
        ).to(self.device)
