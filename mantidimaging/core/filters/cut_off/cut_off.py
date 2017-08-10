from __future__ import (absolute_import, division, print_function)
from mantidimaging import helper as h
import numpy as np


def _cli_register(parser):
    parser.add_argument(
        "--cut-off",
        required=False,
        type=float,
        default=None,
        help="Cut off values above threshold relative to the max pixels. "
        "The threshold must be in range 0 < threshold < 1. "
        "Example: --cut-off 0.95")

    return parser


def _gui_register(main_window):
    from mantidimaging.core.algorithms import gui_compile_ui as gcu
    from mantidimaging.gui.algorithm_dialog import AlgorithmDialog
    from PyQt5 import Qt
    dialog = AlgorithmDialog(main_window)
    gcu.execute("gui/ui/alg_dialog.ui", dialog)
    dialog.setWindowTitle("Cut Off")

    label_radius = Qt.QLabel("Threshold")
    radius_field = Qt.QDoubleSpinBox()
    radius_field.setMinimum(0)
    radius_field.setMaximum(1)
    radius_field.setValue(0.95)

    dialog.formLayout.addRow(label_radius, radius_field)

    def decorate_execute():
        from functools import partial
        return partial(execute, threshold=radius_field.value())

    # replace dialog function with this one
    dialog.decorate_execute = decorate_execute
    return dialog


def execute(data, threshold):
    """
    Execute the Cut off filter.
    Cut off values above threshold relative to the max pixels.

    :param data: Input data as a 3D numpy.ndarray

    :param threshold: The threshold related to the minimum pixel value that will be clipped

    :return: The processed 3D numpy.ndarray

    Example command line:
    mantidimaging -i /some/data/ --cut-off 0.95
    """

    if threshold and threshold > 0.0:
        dmin = np.amin(data)
        dmax = np.amax(data)
        h.pstart(
            "Applying cut-off with level: {0}, min value {1}, max value {2}".
            format(threshold, dmin, dmax))
        rel_cut_off = dmin + threshold * (dmax - dmin)

        np.minimum(data, rel_cut_off, out=data)

        h.pstop("Finished cut-off step, with pixel data type: {0}.".format(
            data.dtype))

    return data