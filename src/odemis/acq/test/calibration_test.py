# -*- coding: utf-8 -*-
'''
Created on 3 Mar 2014

@author: Éric Piel

Copyright © 2014 Éric Piel, Delmic

This file is part of Odemis.

Odemis is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License version 2 as published by the Free Software Foundation.

Odemis is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with Odemis. If not, see http://www.gnu.org/licenses/.
'''
from __future__ import division

import logging
import numpy
from odemis import model, dataio
from odemis.acq import calibration
from odemis.util import img
import os
import time
import unittest


logging.getLogger().setLevel(logging.DEBUG)


class TestAR(unittest.TestCase):
    """
    Test the AR related functions
    """

    def test_load_simple(self):
        # AR background data
        dcalib = numpy.zeros((512, 1024), dtype=numpy.uint16)
        md = {model.MD_SW_VERSION: "1.0-test",
             model.MD_HW_NAME: "fake ccd",
             model.MD_DESCRIPTION: "AR",
             model.MD_ACQ_DATE: time.time(),
             model.MD_BPP: 12,
             model.MD_BINNING: (1, 1), # px, px
             model.MD_SENSOR_PIXEL_SIZE: (13e-6, 13e-6), # m/px
             model.MD_PIXEL_SIZE: (1e-6, 2e-5), # m/px
             model.MD_POS: (1.2e-3, -30e-3), # m
             model.MD_EXP_TIME: 1.2, # s
             model.MD_AR_POLE: (253.1, 65.1),
             model.MD_LENS_MAG: 60, # ratio
            }
        calib = model.DataArray(dcalib, md)

        # Give one DA, the correct one, so expect to get it back
        out = calibration.get_ar_data([calib])
        numpy.testing.assert_equal(out, calib)

        # More DataArrays, just to make it slightly harder to find the data
        data1 = model.DataArray(numpy.ones((1, 1, 1, 520, 230), dtype=numpy.uint16),
                                metadata={model.MD_POS: (1.2e-3, -30e-3)})
        data2 = model.DataArray(17 * numpy.ones((1, 1), dtype=numpy.uint16),
                                metadata={model.MD_POS: (1.2e-3, -30e-3)})
        out = calibration.get_ar_data([data1, calib, data2])
        numpy.testing.assert_equal(out, calib)

    def test_load_full(self):
        """
        Check the whole sequence: saving calibration data to file, loading it 
        back from file, finding it.
        """
        # AR background data
        dcalib = numpy.zeros((512, 1024), dtype=numpy.uint16)
        md = {model.MD_SW_VERSION: "1.0-test",
             model.MD_HW_NAME: "fake ccd",
             model.MD_DESCRIPTION: "AR",
             model.MD_ACQ_DATE: time.time(),
             model.MD_BPP: 12,
             model.MD_BINNING: (1, 1), # px, px
             model.MD_SENSOR_PIXEL_SIZE: (13e-6, 13e-6), # m/px
             model.MD_PIXEL_SIZE: (1e-6, 2e-5), # m/px
             model.MD_POS: (1.2e-3, -30e-3), # m
             model.MD_EXP_TIME: 1.2, # s
             model.MD_AR_POLE: (253.1, 65.1),
             model.MD_LENS_MAG: 60, # ratio
            }
        calib = model.DataArray(dcalib, md)

        # Give one DA, the correct one, so expect to get it back
        out = calibration.get_ar_data([calib])
        numpy.testing.assert_equal(out, calib)

        # More DataArrays, just to make it slightly harder to find the data
        data1 = model.DataArray(numpy.ones((1, 1, 1, 520, 230), dtype=numpy.uint16),
                                metadata={model.MD_POS: (1.2e-3, -30e-3)})
        data2 = model.DataArray(17 * numpy.ones((1, 1), dtype=numpy.uint16),
                                metadata={model.MD_POS: (1.2e-3, -30e-3)})
        # RGB image
        thumb = model.DataArray(numpy.ones((520, 230, 3), dtype=numpy.uint8))

        full_data = [data1, calib, data2]

        for fmt in dataio.get_available_formats():
            exporter = dataio.get_exporter(fmt)
            logging.info("Trying to export/import with %s", fmt)
            fn = u"test_ar" + exporter.EXTENSIONS[0]
            exporter.export(fn, full_data, thumb)

            idata = exporter.read_data(fn)
            icalib = calibration.get_ar_data(idata)
            icalib2d = img.ensure2DImage(icalib)
            numpy.testing.assert_equal(icalib2d, calib)
            numpy.testing.assert_almost_equal(icalib.metadata[model.MD_AR_POLE],
                                              calib.metadata[model.MD_AR_POLE])
            os.remove(fn)


class TestSpectrum(unittest.TestCase):
    """
    Test the Spectrum related functions
    """
    
    
    def test_load_simple(self):
        # Compensation data
        dcalib = numpy.array([1, 1.3, 2, 3.5, 4, 5, 0.1, 6, 9.1], dtype=numpy.float)
        dcalib.shape = (dcalib.shape[0], 1, 1, 1, 1)
        wl_calib = 400e-9 + numpy.array(range(dcalib.shape[0])) * 10e-9
        calib = model.DataArray(dcalib, metadata={model.MD_WL_LIST: wl_calib})

        # Give one DA, the correct one, so expect to get it back
        out = calibration.get_spectrum_efficiency([calib])
        numpy.testing.assert_equal(out, calib)
        numpy.testing.assert_almost_equal(out.metadata[model.MD_WL_LIST],
                                          calib.metadata[model.MD_WL_LIST])

        # More DataArrays, just to make it slightly harder to find the data
        data1 = model.DataArray(numpy.ones((1, 1, 1, 520, 230), dtype=numpy.uint16))
        out = calibration.get_spectrum_efficiency([data1, calib])
        numpy.testing.assert_equal(out, calib)
        numpy.testing.assert_almost_equal(out.metadata[model.MD_WL_LIST],
                                          calib.metadata[model.MD_WL_LIST])

    def test_load_full(self):
        """
        Check the whole sequence: saving calibration data to file, loading it 
        back from file, finding it.
        """
        # Compensation data
        dcalib = numpy.array([1, 1.3, 2, 3.5, 4, 5, 0.1, 6, 9.1], dtype=numpy.float)
        dcalib.shape = (dcalib.shape[0], 1, 1, 1, 1)
        wl_calib = 400e-9 + numpy.array(range(dcalib.shape[0])) * 10e-9
        calib = model.DataArray(dcalib, metadata={model.MD_WL_LIST: wl_calib})

        # More DataArrays, just to make it slightly harder to find the data
        data1 = model.DataArray(numpy.ones((1, 1, 1, 520, 230), dtype=numpy.uint16))
        data2 = model.DataArray(numpy.zeros((3, 1, 1, 520, 230), dtype=numpy.uint16))

        # RGB image
        thumb = model.DataArray(numpy.ones((520, 230, 3), dtype=numpy.uint8))
        
        full_data = [data1, calib, data2]

        for fmt in dataio.get_available_formats():
            exporter = dataio.get_exporter(fmt)
            logging.info("Trying to export/import with %s", fmt)
            fn = u"test_spec" + exporter.EXTENSIONS[0]
            exporter.export(fn, full_data, thumb)

            idata = exporter.read_data(fn)
            icalib = calibration.get_spectrum_efficiency(idata)
            numpy.testing.assert_equal(icalib, calib)
            numpy.testing.assert_almost_equal(icalib.metadata[model.MD_WL_LIST],
                                              calib.metadata[model.MD_WL_LIST])
            os.remove(fn)

    
    def test_compensate(self):
        """Test applying efficiency compensation"""
        # Spectrum
        data = numpy.ones((251, 1, 1, 200, 300), dtype="uint16")
        wld = 433e-9 + numpy.array(range(data.shape[0])) * 0.1e-9
        spec = model.DataArray(data, metadata={model.MD_WL_LIST: wld})
        
        # Compensation data
        dcalib = numpy.array([1, 1.3, 2, 3.5, 4, 5, 0.1, 6, 9.1], dtype=numpy.float)
        dcalib.shape = (dcalib.shape[0], 1, 1, 1, 1)
        wl_calib = 400e-9 + numpy.array(range(dcalib.shape[0])) * 10e-9
        calib = model.DataArray(dcalib, metadata={model.MD_WL_LIST: wl_calib})

        compensated = calibration.compensate_spectrum_efficiency(spec, calib)

        self.assertEqual(spec.shape, compensated.shape)
        numpy.testing.assert_equal(spec.metadata[model.MD_WL_LIST],
                                   compensated.metadata[model.MD_WL_LIST])
        
        for i in range(dcalib.shape[0] - 1):
            ca, cb = calib[i], calib[i + 1]
            wla, wlb = wl_calib[i], wl_calib[i + 1]
            # All the values between the 2 wavelengths should be compensated
            # between the 2 factors

            for vo, vc, wl in zip(spec[..., 3, 3], compensated[..., 3, 3], wld):
                if wla <= wl <= wlb:
                    expa, expb = ca * vo, cb * vo
                    minc, maxc = min(expa, expb), max(expa, expb)
                    self.assertTrue(minc <= vc <= maxc)

    def test_compensate_out(self):
        """Test applying efficiency compensation on an edge of calibration"""
        # Spectrum
        data = numpy.ones((251, 1, 1, 200, 300), dtype="uint16")
        wld = 333e-9 + numpy.array(range(data.shape[0])) * 0.1e-9
        spec = model.DataArray(data, metadata={model.MD_WL_LIST: wld})
        
        # Only from 400 nm => need to use the border (=1) for everything below
        dcalib = numpy.array([1, 1, 2, 3, 4, 5, 1, 6, 9], dtype=numpy.float)
        dcalib.shape = (dcalib.shape[0], 1, 1, 1, 1)
        wl_calib = 400e-9 + numpy.array(range(dcalib.shape[0])) * 10e-9
        calib = model.DataArray(dcalib, metadata={model.MD_WL_LIST: wl_calib})

        compensated = calibration.compensate_spectrum_efficiency(spec, calib)
        
        self.assertEqual(spec.shape, compensated.shape)
        numpy.testing.assert_equal(spec.metadata[model.MD_WL_LIST],
                                   compensated.metadata[model.MD_WL_LIST])

        # Value before the first calibration wavelength must be estimated
        for vo, vc, wl in zip(spec[..., 3, 3], compensated[..., 3, 3], wld):
            if wl <= wl_calib[0]:
                self.assertEqual(vo * dcalib[0], vc)

if __name__ == "__main__":
    unittest.main()
