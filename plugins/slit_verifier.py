# -*- coding: utf-8 -*-
"""
Created on 10 July 2023
@author: Canberk Akın
Runs procedures acquire an image of the slit and verifies that the image is focused via a button under Help > Development
Copyright © 2023 Canberk Akın, Delmic
This file is part of Odemis.
Odemis is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License version 2 as published by the Free Software Foundation.
Odemis is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even
the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
Public License for more details.
You should have received a copy of the GNU General Public License along with Odemis. If not,
see http://www.gnu.org/licenses/.
"""
import logging
import os
import time
import wx

from datetime import datetime

from odemis import dataio, model
from odemis.acq import acqmng, path
from odemis.acq.align.autofocus import (Sparc2ManualFocus, _getSpectrometerFocusingComponents)
from odemis.dataio import tiff
from odemis.gui.comp import popup
from odemis.gui.plugin import Plugin


now = datetime.now()
tfn = now.strftime("%Y%m%d-%H%M%S")
REPORT_FILE = os.path.expanduser('~') +'/Desktop/Reports/slit_verifier_report-%s.txt' % tfn

class AutofocusVerifierPlugin(Plugin):
    name = "Slit Verifier"
    __version__ = "1.0"
    __author__ = "Canberk Akın"
    __license__ = "GPL2"

    def __init__(self, microscope, main_app):
        super().__init__(microscope, main_app)

        self.addMenu("Help/Development/Verify slit", self.show_acquisition)

        self.tab = self.main_app.main_data.getTabByName("sparc_acqui")
        self.tab_data = self.tab.tab_data_model

        self._mf_future = None

        self.main = self.tab_data.main
        self.bl = self.main.brightlight

        self.ccd = self.main.ccd
        self.opm = path.OpticalPathManager(self.microscope)
        # self.opm = self.main.OpticalPathManager(self.microscope)
        self.spectrograph = self.main.spectrograph

        # self.slit_in_big = model.getComponent(role="slit-in-big")
        # self.slit_in_big = self.main_app.main_data.slit_in_big

    def show_acquisition(self):
        """
        Shows the alignment tab with a little bit of delay to ensure the buttons can be found by the plugin.
        """
        alignment_tab = self.main_app.main_data.getTabByName('sparc_acqui')
        self.main_app.main_data.tab.value = alignment_tab

        wx.CallLater(500, self.verify_slit)

    def verify_slit(self):
        """
        Initiates the slit verification process.
        """
        acqui_tab = self.main_app.main_data.getTabByName("sparc_acqui")
        acqui_tab.streambar_controller.pauseStreams()

        # turn on the calibration light
        self.bl.power.value = self.bl.power.range[1]

        # f = self.opm.setPath("mirror-align", self.ccd)
        f = self.main.opm.setPath("mirror-align", self.ccd)
        f.add_done_callback(self.acquire_slit_image)

        ccd_image = self.ccd.data.get(asap=False)
        tiff.export(os.path.join(IMAGE_PATH, '%s-bright.tiff' % tfn), ccd_image)

    def acquire_slit_image(self, future):
        """
        Moves the slit to open, small and minimal positions and acquire image per movement
        """
        # TODO: define a function that takes an opening as an argument
        #  acquire the image based on the slit opening
        logging.debug("AAAA acq slit img")
        slit_positions = ["fully_open", "small_open", "minimal_open"]
        for opening in slit_positions: # list of values like 1000, 500, 200, 0:
            ...
            # TODO: call the function and pass opening as argument

            for position, name in self.main_app.main_data.slit_in_big.axes["x"].choices.items():
                if name == "off":
                    f = self.main_app.main_data.slit_in_big.moveAbs({"x" : position})

                    # f.result()
                    f.add_done_callback(self.on_slit_movement_done)

    def on_slit_movement_done(self, future):
        logging.debug("AAAA on slit mov done")

        # Save the opening to a text file
        with open('slit_openings.txt', 'w') as f:
            f.write('Opening :' + '\n')
            for opening in slit_positions:
                f.write(str(opening) + '\n')
