"""
Contains the core of artist: Artist, Plotter.

NOTE: this module is private. All functions and objects are available in the main
`dataplot` namespace - use that instead.

"""

from collections import Counter
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Optional

from ..container import FigWrapper
from ..setting import PlotSettable
from ..utils.multi import multiple

if TYPE_CHECKING:
    from numpy.typing import NDArray

    from ..container import AxesWrapper

__all__ = ["Artist", "Plotter"]


@dataclass(slots=True)
class Artist(PlotSettable):
    """
    Paint the desired images on an axes.

    Parameters
    ----------
    plotter : Plotter
        Painting tool.

    """

    plotter: "Plotter"

    def __repr__(self) -> str:
        names = (x.__class__.__name__ for x in multiple(self.plotter))
        s = ", ".join(f"{i} {x}s" for x, i in Counter(names).items())
        return f"<{self.__class__.__name__} with {s}>"

    def paint(self, ax: Optional["AxesWrapper"] = None) -> None:
        """
        Paint on the axes.

        Parameters
        ----------
        ax : AxesWrapper, optional
            Specifies the axes-wrapper on which the plot should be painted,
            by default None.

        """
        with self.customize(FigWrapper, 1, 1, active := ax is None) as fig:
            self.plotter.paint(fig.axes[0] if active else ax)


@dataclass(slots=True, init=False)
class Plotter(PlotSettable):
    """
    Painting tool used by Artist - user can ignore this.

    """

    data: Optional["NDArray"] = field(repr=False, default=None, init=False)
    label: Optional[str] = field(default=None, init=False)

    def paint(
        self,
        ax: "AxesWrapper",
        *,
        __multi_prev_returned__: Any = None,
        __multi_is_final__: bool = True,
    ) -> Any:
        """Paint."""
