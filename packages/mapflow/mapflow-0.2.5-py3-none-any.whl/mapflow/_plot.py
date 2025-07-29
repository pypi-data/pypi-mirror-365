from copy import copy
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from matplotlib.collections import PatchCollection
from matplotlib.colors import LogNorm, Normalize
from matplotlib.patches import Polygon as PolygonPatch
from pyproj import CRS
from shapely.geometry import MultiPolygon

from ._misc import X_NAME_CANDIDATES, Y_NAME_CANDIDATES, guess_coord_name, process_crs


class PlotModel:
    def __init__(self, x, y, crs=4326, borders=None):
        """
        Initializes the PlotModel.

        Args:
            x, y: Coordinates for the plot.
            crs: Coordinate Reference System. Defaults to 4326.
            borders (gpd.GeoDataFrame | gpd.GeoSeries | None): Custom borders to use.
                If None, defaults to world borders from a packaged GeoPackage.
        """
        self.x = np.asarray_chkfinite(x)
        self.y = np.asarray_chkfinite(y)
        if self.x.ndim != self.y.ndim:
            raise ValueError("x and y must have the same dimensionality (both 1D or both 2D)")

        self.crs = CRS.from_user_input(crs)
        if self.crs.is_geographic:
            self.aspect = 1 / np.cos((self.y.mean() * np.pi / 180))
        else:
            self.aspect = 1
        if self.x.ndim == 1:
            self.dx = abs(self.x[1] - self.x[0])
            self.dy = abs(self.y[1] - self.y[0])
        else:
            self.dx = np.diff(self.x, axis=1).max()
            self.dy = np.diff(self.y, axis=0).max()
        bbox = (
            self.x.min() - 10 * self.dx,
            self.y.min() - 10 * self.dy,
            self.x.max() + 10 * self.dx,
            self.y.max() + 10 * self.dy,
        )

        if borders is None:
            borders_ = gpd.read_file(Path(__file__).parent / "_static" / "world.gpkg")
        elif isinstance(borders, (gpd.GeoDataFrame, gpd.GeoSeries)):
            borders_ = borders
        else:
            raise TypeError("borders must be a geopandas GeoDataFrame, GeoSeries, or None.")
        borders_ = borders_.to_crs(self.crs).clip(bbox)
        self.borders = self._shp_to_patches(borders_)

    @staticmethod
    def _shp_to_patches(gdf):
        patches = []
        for poly in gdf.geometry.values:
            if isinstance(poly, MultiPolygon):
                for polygon in poly.geoms:
                    patches.append(PolygonPatch(polygon.exterior.coords))
            else:
                patches.append(PolygonPatch(poly.exterior.coords))
        return PatchCollection(patches, facecolor="none", linewidth=0.5, edgecolor="k")

    @staticmethod
    def _norm(data, vmin, vmax, qmin, qmax, norm, log):
        """Generates a normalization based on the specified parameters.

        Args:
            data (array-like): Data to normalize.
            vmin (float): Minimum value for normalization.
            vmax (float): Maximum value for normalization.
            qmin (float): Minimum quantile for normalization.
            qmax (float): Maximum quantile for normalization.
            norm (matplotlib.colors.Normalize): Custom normalization object.
            log (bool): Indicates if a logarithmic scale should be used.

        Returns:
            matplotlib.colors.Normalize: Normalization object.

        """
        if norm is not None:
            return norm
        if log:
            vmin = np.nanpercentile(data[data > 0], q=qmin) if vmin is None else vmin
            vmax = np.nanpercentile(data[data > 0], q=qmax) if vmax is None else vmax
            return LogNorm(vmin=vmin, vmax=vmax)
        vmin = np.nanpercentile(data, q=qmin) if vmin is None else vmin
        vmax = np.nanpercentile(data, q=qmax) if vmax is None else vmax
        return Normalize(vmin=vmin, vmax=vmax)

    def _process_data(self, data):
        if not isinstance(data, np.ndarray):
            data = np.asarray(data)
        data = np.squeeze(data)
        if data.ndim != 2:
            raise ValueError("Data must be a 2D array.")
        if data.shape[0] != self.y.size or data.shape[1] != self.x.size:
            raise ValueError("Data shape does not match x and y dimensions.")
        return data

    def __call__(
        self,
        data,
        figsize=None,
        qmin=0.01,
        qmax=99.9,
        vmin=None,
        vmax=None,
        log=False,
        cmap="jet",
        norm=None,
        shading="nearest",
        shrink=0.4,
        label=None,
        title=None,
        show=True,
    ):
        """
        Plots a 2D data array using pcolormesh.

        This method handles the actual plotting of a single frame. It applies
        normalization, colormaps, adds a colorbar, overlays borders, sets the
        aspect ratio, title, and optionally displays the plot.

        Args:
            data (np.ndarray): 2D array of data to plot.
            figsize (tuple[float, float], optional): Figure size (width, height)
                in inches. Defaults to None (matplotlib's default).
            qmin (float, optional): Minimum quantile for color normalization if
                vmin is not set. Defaults to 0.01.
            qmax (float, optional): Maximum quantile for color normalization if
                vmax is not set. Defaults to 99.9.
            vmin (float, optional): Minimum value for color normalization.
                Overrides qmin. Defaults to None.
            vmax (float, optional): Maximum value for color normalization.
                Overrides qmax. Defaults to None.
            log (bool, optional): Whether to use a logarithmic color scale.
                Defaults to False.
            cmap (str, optional): Colormap to use. Defaults to "jet".
            norm (matplotlib.colors.Normalize, optional): Custom normalization object.
                Overrides vmin, vmax, qmin, qmax, log. Defaults to None.
            shading (str, optional): Shading method for pcolormesh.
                Defaults to "nearest".
            shrink (float, optional): Factor by which to shrink the colorbar.
                Defaults to 0.4.
            label (str, optional): Label for the colorbar. Defaults to None.
            title (str, optional): Title for the plot. Defaults to None.
            show (bool, optional): Whether to display the plot using `plt.show()`.
                Defaults to True.
        """
        data = self._process_data(data)
        norm = self._norm(data, vmin, vmax, qmin, qmax, norm, log=log)
        plt.figure(figsize=figsize)
        if (self.x.ndim == 1) and (self.y.ndim == 1):
            plt.imshow(
                X=data,
                cmap=cmap,
                norm=norm,
                origin="lower",
                extent=(
                    self.x.min() - self.dx / 2,
                    self.x.max() + self.dx / 2,
                    self.y.min() - self.dy / 2,
                    self.y.max() + self.dy / 2,
                ),
                interpolation=shading,
            )
        else:
            plt.pcolormesh(
                self.x,
                self.y,
                data,
                cmap=cmap,
                norm=norm,
                shading=shading,
                rasterized=True,
            )
        plt.colorbar(shrink=shrink, label=label)
        plt.xlim(self.x.min() - self.dx / 2, self.x.max() + self.dx / 2)
        plt.ylim(self.y.min() - self.dy / 2, self.y.max() + self.dy / 2)
        plt.gca().add_collection(copy(self.borders))
        plt.gca().set_aspect(self.aspect)
        plt.title(title)
        plt.gca().axis("off")
        plt.tight_layout()
        if show:
            plt.show()


def plot_da(da: xr.DataArray, x_name=None, y_name=None, crs=4326, **kwargs):
    actual_x_name = guess_coord_name(da.coords, X_NAME_CANDIDATES, x_name, "x")
    actual_y_name = guess_coord_name(da.coords, Y_NAME_CANDIDATES, y_name, "y")

    da = da.sortby(actual_x_name).sortby(actual_y_name)
    crs_ = process_crs(da, crs)
    if crs_.is_geographic:
        da[actual_x_name] = xr.where(da[actual_x_name] > 180, da[actual_x_name] - 360, da[actual_x_name])

    p = PlotModel(x=da[actual_x_name].values, y=da[actual_y_name].values, crs=crs)
    data = p._process_data(da.values)
    p(data, **kwargs)
