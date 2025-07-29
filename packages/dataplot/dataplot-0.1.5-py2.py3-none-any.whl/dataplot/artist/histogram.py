"""
Contains a plotter class: Histogram.

NOTE: this module is private. All functions and objects are available in the main
`dataplot` namespace - use that instead.

"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

import numpy as np
from scipy import stats

from .base import Plotter

if TYPE_CHECKING:
    from ..container import AxesWrapper

__all__ = ["Histogram"]


@dataclass(slots=True)
class Histogram(Plotter):
    """
    A plotter class that creates a histogram.

    """

    bins: int | list[float]
    fit: bool
    density: bool
    log: bool
    same_bin: bool
    stats: bool

    def paint(
        self,
        ax: "AxesWrapper",
        __multi_prev_returned__: Optional[tuple[str, list[float]]] = None,
        __multi_is_final__: bool = True,
    ) -> list[float]:
        ax.set_default(
            title="Histogram",
            alpha=0.8,
            xlabel="value",
            ylabel="density" if self.density else "count",
        )
        ax.load(self.settings)
        if __multi_prev_returned__ is None:
            xlabel, bins = ax.settings.xlabel, None
        else:
            xlabel, bins = __multi_prev_returned__
        ds, new_bins = self.__hist(
            ax, bins=self.bins if (bins is None or not self.same_bin) else bins
        )
        if self.stats:
            xlabel += "\n" + ds
        if __multi_is_final__:
            ax.set_axes(xlabel=xlabel)
        return (xlabel, new_bins)

    def __hist(
        self, ax: "AxesWrapper", bins: int | list[float] = 100
    ) -> tuple[str, list[float]]:
        _, bin_list, _ = ax.ax.hist(
            self.data,
            bins=bins,
            density=self.density,
            log=self.log,
            alpha=ax.settings.alpha,
            label=self.label,
        )
        mean, std = np.nanmean(self.data), np.nanstd(self.data)
        skew: float = stats.skew(self.data, bias=False, nan_policy="omit")
        kurt: float = stats.kurtosis(self.data, bias=False, nan_policy="omit")
        if self.fit and self.density:
            ax.ax.plot(
                bin_list,
                stats.norm.pdf(bin_list, mean, std),
                alpha=ax.settings.alpha,
                label=f"{self.label} · fit",
            )
        return (
            f"{self.label}: mean={mean:.3f}, std={std:.3f}, skew={skew:.3f}, "
            f"kurt={kurt:.3f}",
            bin_list,
        )
