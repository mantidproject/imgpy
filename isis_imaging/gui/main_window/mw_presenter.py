from __future__ import absolute_import, division, print_function

import os

from enum import IntEnum

from core.imgdata import loader
from gui.main_window.mw_model import ImgpyMainWindowModel


class Notification(IntEnum):
    MEDIAN_FILTER_CLICKED = 1


class ImgpyMainWindowPresenter(object):

    def __init__(self, view, config):
        super(ImgpyMainWindowPresenter, self).__init__()
        self.view = view
        self.config = config
        self.model = ImgpyMainWindowModel()

    def notify(self, signal):
        # do some magical error message reusal
        # try:
        # except any error:
        # show error message from the CORE, no errors will be written here!
        try:  # this is very very bad, it completely fucks the stacks trace!
            if signal == Notification.MEDIAN_FILTER_CLICKED:
                self.update_view_value()
            elif signal == Notification.LOAD:
                self.load_stack()
        except Exception as e:
            self.show_error(e)
            raise  # re-raise for full stack trace

    def show_error(self, error):
        print("Magic to be done here")

    def load_stack(self):
        # save to model for future runs? or keep getting the value from the dialogue? less places to update
        # because we will HAVE to build a command line for remote submission,
        # which will use the model?
        self.model.sample_path = self.view.load_dialogue.sample_path()
        # TODO cache the flat and dark
        self.model.flat_path = self.view.load_dialogue.flat_path()
        self.model.dark_path = self.view.load_dialogue.dark_path()
        self.model.img_format = self.view.load_dialogue.img_extension
        self.model.parallel_load = self.view.load_dialogue.parallel_load()
        self.model.indices = self.view.load_dialogue.indices()

        if not self.model.sample_path:
            return

        stack = loader.load(
            self.model.sample_path,
            None,
            None,
            self.model.img_format,
            parallel_load=self.model.parallel_load,
            indices=self.model.indices)

        self.view.add_stack_dock(
            stack, title=os.path.basename(self.model.sample_path))
