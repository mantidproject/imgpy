from __future__ import absolute_import, division, print_function

from logging import getLogger
from PyQt5 import Qt, QtCore
from PyQt5 import Qt, QtCore, QtWidgets

from mantidimaging.core.algorithms import gui_compile_ui
from mantidimaging.gui.stack_visualiser.sv_view import StackVisualiserView

from .load_dialog import MWLoadDialog
from .mw_presenter import MainWindowPresenter
from .mw_presenter import Notification as PresNotification
from .save_dialog import MWSaveDialog


class MainWindowView(Qt.QMainWindow):
    def __init__(self, config):
        super(MainWindowView, self).__init__()
        gui_compile_ui.execute('gui/ui/main_window.ui', self)

        self.setup_shortcuts()

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("MantidImaging")

        # filter and algorithm communications will be funneled through this
        self.presenter = MainWindowPresenter(self, config)

    def setup_shortcuts(self):
        self.actionLoad.setShortcut('F1')
        self.actionLoad.triggered.connect(self.show_load_dialogue)

        self.actionSave.setShortcut('Ctrl+S')
        self.actionSave.triggered.connect(self.show_save_dialogue)

        self.actionExit.setShortcut('Ctrl+Q')
        self.actionExit.triggered.connect(Qt.qApp.quit)

    def show_load_dialogue(self):
        self.load_dialogue = MWLoadDialog(self)
        self.load_dialogue.show()

    def execute_save(self):
        self.presenter.notify(PresNotification.SAVE)

    def execute_load(self):
        self.presenter.notify(PresNotification.LOAD)

    def show_save_dialogue(self):
        self.save_dialogue = MWSaveDialog(self, self.stack_list())
        self.save_dialogue.show()

    def stack_names(self):
        # unpacks the tuple and only gives the correctly sorted human readable names
        return self.presenter.stack_names()

    def stack_list(self):
        return self.presenter.stack_list()

    def create_stack_window(self,
                            stack,
                            title,
                            position=QtCore.Qt.TopDockWidgetArea,
                            floating=False):
        dock_widget = Qt.QDockWidget(title, self)

        # this puts the new stack window into the centre of the window
        self.setCentralWidget(dock_widget)

        # add the dock widget into the main window
        self.addDockWidget(position, dock_widget)

        # we can get the stack visualiser widget with dock_widget.widget
        dock_widget.setWidget(
            StackVisualiserView(self, dock_widget, stack))

        # proof of concept above
        assert isinstance(
            dock_widget.widget(), StackVisualiserView
        ), "Widget inside dock_widget is not an StackVisualiserView!"

        dock_widget.setFloating(floating)

        return dock_widget

    def remove_stack(self, obj):
        getLogger(__name__).debug("Removing stack with uuid {}".format(obj.uuid))
        self.presenter.remove_stack(obj.uuid)

    def algorithm_accepted(self, stack_uuid, algorithm_dialog):
        """
        We forward the data onwards to the presenter and then the model, so that we can have a passive view.

        :param stack_uuid: The unique ID of the stack

        :param algorithm_dialog: The algorithm dialog object
        """
        self.presenter.apply_to_data(stack_uuid, algorithm_dialog)

    def show_error_dialog(self, msg=""):
        """
        Shows an error message.

        :param msg: Error message string
        """
        QtWidgets.QMessageBox.critical(self, "Error", msg)
