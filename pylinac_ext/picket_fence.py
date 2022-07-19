from pylinac.settings import get_dicom_cmap
from typing import Union, Tuple, List, Optional, BinaryIO, Iterable, Sequence
from pylinac.picketfence import PicketFence, Orientation

import matplotlib.pyplot as plt


def plot_analyzed_image(pf: PicketFence, guard_rails: bool = True, mlc_peaks: bool = True, overlay: bool = True,
                        leaf_error_subplot: bool = True, show: bool = False,
                        figure_size: Union[str, Tuple] = 'auto'):

    # plot the image
    if figure_size == 'auto':
        if pf.orientation == Orientation.UP_DOWN:
            figure_size = (12, 8)
        else:
            figure_size = (9, 9)
    fig, ax = plt.subplots(figsize=figure_size)
    ax.imshow(pf.image.array, cmap=get_dicom_cmap())

    if leaf_error_subplot:
        pf._add_leaf_error_subplot(ax)

    if guard_rails:
        for picket in pf.pickets:
            picket.add_guards_to_axes(ax.axes)
    if mlc_peaks:
        for mlc_meas in pf.mlc_meas:
            mlc_meas.plot2axes(ax.axes, width=1.5)

    if overlay:
        for mlc_meas in pf.mlc_meas:
            mlc_meas.plot_overlay2axes(ax.axes)

    # plot CAX
    ax.plot(pf.image.center.x, pf.image.center.y, 'r+', ms=12, markeredgewidth=3)

    # tighten up the plot view
    ax.set_xlim([0, pf.image.shape[1]])
    ax.set_ylim([0, pf.image.shape[0]])
    ax.axis('off')

    if show:
        plt.show()

    return fig