"""The sgp4.py module.

This module provides the `SGP4` class.
"""

from typing import Literal

import lox_space as lox
from pydantic import Field, PrivateAttr

from ephemerista import get_eop_provider
from ephemerista.coords.trajectories import Trajectory
from ephemerista.coords.twobody import Cartesian
from ephemerista.propagators import Propagator
from ephemerista.time import Time


class SGP4(Propagator):
    """The SGP4 class propagates orbits defined as Two-Line Element (TLE) sets."""

    propagator_type: Literal["sgp4"] = Field(
        default="sgp4", frozen=True, repr=False, alias="type", description="The type of the propagator"
    )
    tle: str
    _sgp4: lox.SGP4 = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._sgp4 = lox.SGP4(self.tle)

    def propagate(self, time: Time | list[Time]) -> Cartesian | Trajectory:  # type: ignore
        """
        Propagate the state.

        Parameters
        ----------
        time: Time | list[Time]
            Either a single `Time` or a list of `Time` objects.

        Returns
        -------
        Cartesian | Trajectory
            Either a single `Cartesian` state for a discrete input or a `Trajectory` for a list.
        """
        if isinstance(time, Time):
            return Cartesian._from_lox(self._sgp4.propagate(time._time, get_eop_provider()))  # type: ignore
        times = [t._time for t in time]
        return Trajectory._from_lox(self._sgp4.propagate(times, get_eop_provider()))  # type: ignore

    @property
    def time(self) -> Time:
        """Time: Epoch of the TLE set."""
        return Time._from_lox(self._sgp4.time())
