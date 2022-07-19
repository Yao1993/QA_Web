from unittest import result
import matplotlib.pyplot as plt
from pylinac.settings import get_dicom_cmap
from pylinac.ct import CTP486, CTP528CP504, CTP515


def plot_analyzed_image(catphan, show: bool = False, **plt_kwargs) -> None:
    """Plot the images used in the calculation and summary data.

    Parameters
    ----------
    show : bool
        Whether to plot the image or not.
    plt_kwargs : dict
        Keyword args passed to the plt.figure() method. Allows one to set things like figure size.
    """
    def plot(ctp_module, axis, vmin=None, vmax=None):
        axis.imshow(ctp_module.image.array, cmap=get_dicom_cmap(), vmin=vmin, vmax=vmax)
        ctp_module.plot_rois(axis)
        axis.autoscale(tight=True)
        axis.set_title(ctp_module.common_name)
        axis.axis('off')

    # set up grid and axes
    plt.figure(**plt_kwargs)
    grid_size = (2, 4)
    hu_ax = plt.subplot2grid(grid_size, (0, 1))
    plot(catphan.ctp404, hu_ax)
    hu_lin_ax = plt.subplot2grid(grid_size, (0, 2))
    catphan.ctp404.plot_linearity(hu_lin_ax)
    if catphan._has_module(CTP486):
        unif_ax = plt.subplot2grid(grid_size, (0, 0))
        plot(catphan.ctp486, unif_ax)
        unif_prof_ax = plt.subplot2grid(grid_size, (1, 2), colspan=2)
        catphan.ctp486.plot_profiles(unif_prof_ax)
    if catphan._has_module(CTP528CP504):
        sr_ax = plt.subplot2grid(grid_size, (1, 0))
        plot(catphan.ctp528, sr_ax)
        mtf_ax = plt.subplot2grid(grid_size, (0, 3))
        catphan.ctp528.plot_mtf(mtf_ax)
    if catphan._has_module(CTP515):
        locon_ax = plt.subplot2grid(grid_size, (1, 1))
        plot(catphan.ctp515, locon_ax, vmin=catphan.ctp515.lower_window, vmax=catphan.ctp515.upper_window)

    # finish up
    plt.tight_layout()
    if show:
        plt.show()

    return plt.gcf()


def get_results(catphan) -> str:
    results = [
        f"- CatPhan {catphan._model} QA Test -",
        f"HU Linearity ROIs: {catphan.ctp404.roi_vals_as_str}",
        f"HU Passed?: {catphan.ctp404.passed_hu}",
        f"Low contrast visibility: {catphan.ctp404.lcv:2.2f}",
        f"Geometric Line Average (mm): {catphan.ctp404.avg_line_length:2.2f}",
        f"Geometry Passed?: {catphan.ctp404.passed_geometry}",
        f"Measured Slice Thickness (mm): {catphan.ctp404.meas_slice_thickness:2.3f}",
        f"Slice Thickness Passed? {catphan.ctp404.passed_thickness}"

    ]

    if catphan._has_module(CTP486):

        add = [
            f"Uniformity ROIs: {catphan.ctp486.roi_vals_as_str}",
            f"Uniformity index: {catphan.ctp486.uniformity_index:2.3f}",
            f"Integral non-uniformity: {catphan.ctp486.integral_non_uniformity:2.4f}",
            f"Uniformity Passed?: {catphan.ctp486.overall_passed}",
        ]
        results.extend(add)

    if catphan._has_module(CTP528CP504):
        add = [f"MTF 50% (lp/mm): {catphan.ctp528.mtf.relative_resolution(50):2.2f}"]
        results.extend(add)
    if catphan._has_module(CTP515):
        add = [f"Low contrast ROIs \"seen\": {catphan.ctp515.rois_visible}"]
        results.extend(add)
    return results