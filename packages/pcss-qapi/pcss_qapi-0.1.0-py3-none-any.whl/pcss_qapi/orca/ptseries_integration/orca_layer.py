""" ORCA layer module """
import numpy as np
import numpy.typing as npt

from ptseries.models.observables import Observable
from ptseries.models import PTLayer
from pcss_qapi.orca.ptseries_integration.pt_adapter import PTAdapter

from pcss_qapi.base.connection_base import ApiConnection


class ORCALayer(PTLayer):

    # pylint:disable = too-few-public-methods
    """Neural Network layer using ORCA quantum computers, a PTLayer wrapper

    Parameters
    ----------
    in_features: int,
        number fo layer input features
    observable: Literal['avg-photons', 'covariances', 'correlations'], default = 'avg-photons'
        method of conversion from measurements to a tensor. Default is "avg-photons".
    gradient_mode: Literal['parameter-shift', 'finite-difference', 'spsa'], default = 'parameter-shift',
        method to compute the gradient. Default is "parameter-shift".
    gradient_delta: float, default = np.pi / 10
        Delta to use with the parameter shift rule or for the finite difference. Default is np.pi / 10.
    n_samples: int, default = 100if url is None or machine is None:
                raise ValueError('Parameters url, machine and secret key need to be provided to use real PT device')

        Number of samples to draw. Default is 100.
    n_tiling: int, default = 1
        Uses n_tiling instances of PT Series and concatenates the results.
        Input features are distributed between tiles, which each have different trainable params. Default is 1.
    input_state: list[int] | tuple[int, ...] | npt.NDArray[np.int_] | None:
        Optional input state to set. If none defaults to [0,1,0,1,...]. Defaults to None.
    url: str, default = None
        The URL of the PT device, for example "http://<orca_api_address>".
    tbi_params: dict, default = None
        Dictionary of optional parameters to instantiate the TBI. Default is None.
    """

    def __init__(
        self,
        connection: ApiConnection,
        in_features: int,
        observable: str | Observable = "avg-photons",
        gradient_mode: str = "parameter-shift",
        gradient_delta: float = np.pi / 10,
        input_state: list[int] | tuple[int, ...] | npt.NDArray[np.int_] | None = None,
        n_samples: int = 100,
        tbi_params: dict | None = None,
        n_tiling: int = 1,
        machine: str | None = None
    ):
        input_state = list(map(lambda x: x % 2, range(in_features + 1))) if input_state is None else input_state
        tbi_params = tbi_params if tbi_params is not None else {}
        super().__init__(
            input_state,
            in_features,
            observable,
            gradient_mode,
            gradient_delta,
            n_samples,
            tbi_params | (
                {'tbi_type': 'single-loop'}
                if tbi_params.get('tbi_type', 'none') not in ['single-loop', 'multi-loop']
                else {}
            ),  # turn off url checking by super constructor
            n_tiling
        )

        if tbi_params.get('tbi_type', None) == 'PT':
            self.tbi = PTAdapter(
                connection,
                machine=machine,
                **({k: v for k, v in tbi_params.items() if v is not None})
            )
