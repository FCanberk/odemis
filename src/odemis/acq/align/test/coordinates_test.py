# -*- coding: utf-8 -*-
'''
Created on 28 Nov 2013

@author: Kimon Tsitsikas

Copyright © 2012-2013 Kimon Tsitsikas, Delmic

This file is part of Odemis.

Odemis is free software: you can redistribute it and/or modify it under the terms 
of the GNU General Public License version 2 as published by the Free Software 
Foundation.

Odemis is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with 
Odemis. If not, see http://www.gnu.org/licenses/.
'''
import logging
import unittest
import numpy

from numpy import random
from random import gauss
from numpy import reshape
from odemis import model
from odemis.dataio import hdf5
from odemis.acq.align import coordinates
from odemis.acq.align import transform
from random import shuffle

logging.getLogger().setLevel(logging.DEBUG)

class TestSpotCoordinates(unittest.TestCase):
    """
    Test SpotCoordinates functions
    """
    @unittest.skip("skip")
    def test_find_center(self):
        """
        Test FindCenterCoordinates
        """
        data = []
        subimages = []

        for i in xrange(10):
            data.append(hdf5.read_data("image" + str(i+1) + ".h5"))
            C, T, Z, Y, X = data[i][0].shape
            data[i][0].shape = Y, X
            subimages.append(data[i][0])

        spot_coordinates = coordinates.FindCenterCoordinates(subimages)
        expected_coordinates = [(4.9998, 4.9768), (5.4181, 4.2244), (15.5542, 15.4534),
                                (8.1512, 8.2081), (5.1537, 4.9287), (5.2221, 5.0449),
                                (4.1433, 6.7063), (6.4313, 7.2690), (4.9355, 5.1400), (5.0209, 4.9929)]
        numpy.testing.assert_almost_equal(spot_coordinates, expected_coordinates, 3)

    @unittest.skip("skip")
    def test_devide_neighborhoods_spot(self):
        """
        Test DivideInNeighborhoods for white spot in black image
        """
        spot_image = numpy.zeros(shape=(256, 256))
        spot_image[112:120, 114:122].fill(255)

        subimages, subimage_coordinates, subimage_size = coordinates.DivideInNeighborhoods(spot_image, (1, 1))
        self.assertEqual(subimages.__len__(), 1)

    @unittest.skip("skip")
    def test_devide_neighborhoods_grid(self):
        """
        Test DivideInNeighborhoods for 3x3 grid of white spots in black image
        """
        grid_image = numpy.zeros(shape=(256, 256))
        x_start, y_start = 70, 64
        for x in xrange(3):
            y_start_in = y_start
            for y in xrange(3):
                grid_image[x_start:x_start + 8, y_start_in:y_start_in + 8].fill(255)
                y_start_in = y_start_in + 40
            x_start = x_start + 40

        subimages, subimage_coordinates, subimage_size = coordinates.DivideInNeighborhoods(grid_image, (3, 3))
        self.assertEqual(subimages.__len__(), 9)

    @unittest.skip("skip")
    def test_devide_neighborhoods_real_sample(self):
        """
        Test DivideInNeighborhoods for one spot real image
        """
        spot_image = hdf5.read_data("single_part.h5")
        C, T, Z, Y, X = spot_image[0].shape
        spot_image[0].shape = Y, X

        subimages, subimage_coordinates, subimage_size = coordinates.DivideInNeighborhoods(spot_image[0], (1, 1))
        self.assertEqual(subimages.__len__(), 1)

    @unittest.skip("skip")
    def test_devide_and_find_center_spot(self):
        """
        Test DivideInNeighborhoods combined with FindCenterCoordinates
        """
        spot_image = hdf5.read_data("single_part.h5")
        C, T, Z, Y, X = spot_image[0].shape
        spot_image[0].shape = Y, X

        subimages, subimage_coordinates, subimage_size = coordinates.DivideInNeighborhoods(spot_image[0], (1, 1))
        spot_coordinates = coordinates.FindCenterCoordinates(subimages)
        optical_coordinates = coordinates.ReconstructImage(subimage_coordinates, spot_coordinates, subimage_size)
        expected_coordinates = [(23, 18)]
        numpy.testing.assert_almost_equal(optical_coordinates, expected_coordinates, 0)

    @unittest.skip("skip")
    def test_devide_and_find_center_grid(self):
        """
        Test DivideInNeighborhoods combined with FindCenterCoordinates
        """
        grid_data = hdf5.read_data("grid_10x10.h5")
        C, T, Z, Y, X = grid_data[0].shape
        grid_data[0].shape = Y, X

        subimages, subimage_coordinates, subimage_size = coordinates.DivideInNeighborhoods(grid_data[0], (10, 10))

        spot_coordinates = coordinates.FindCenterCoordinates(subimages)
        optical_coordinates = coordinates.ReconstructImage(subimage_coordinates, spot_coordinates, subimage_size)

        self.assertEqual(subimages.__len__(), 100)

    @unittest.skip("skip")
    def test_devide_and_find_center_grid_noise(self):
        """
        Test DivideInNeighborhoods combined with FindCenterCoordinates for noisy input
        """
        grid_data = hdf5.read_data("grid_10x10.h5")
        C, T, Z, Y, X = grid_data[0].shape
        grid_data[0].shape = Y, X

        # Add Gaussian noise
        noise = random.normal(0, 40, grid_data[0].size)
        noise_array = noise.reshape(grid_data[0].shape[0], grid_data[0].shape[1])
        noisy_grid_data = grid_data[0] + noise_array

        subimages, subimage_coordinates, subimage_size = coordinates.DivideInNeighborhoods(noisy_grid_data, (10, 10))

        spot_coordinates = coordinates.FindCenterCoordinates(subimages)
        optical_coordinates = coordinates.ReconstructImage(subimage_coordinates, spot_coordinates, subimage_size)

        self.assertEqual(subimages.__len__(), 100)

    @unittest.skip("skip")
    def test_devide_and_find_center_grid_missing_point(self):
        """
        Test DivideInNeighborhoods combined with FindCenterCoordinates for grid that misses one point
        """
        grid_data = hdf5.read_data("grid_missing_point.h5")
        C, T, Z, Y, X = grid_data[0].shape
        grid_data[0].shape = Y, X

        # Add Gaussian noise
        noise = random.normal(0, 40, grid_data[0].size)
        noise_array = noise.reshape(grid_data[0].shape[0], grid_data[0].shape[1])
        noisy_grid_data = grid_data[0] + noise_array

        subimages, subimage_coordinates, subimage_size = coordinates.DivideInNeighborhoods(noisy_grid_data, (10, 10))

        spot_coordinates = coordinates.FindCenterCoordinates(subimages)
        optical_coordinates = coordinates.ReconstructImage(subimage_coordinates, spot_coordinates, subimage_size)

        self.assertEqual(subimages.__len__(), 99)

    @unittest.skip("skip")
    def test_devide_and_find_center_grid_cosmic_ray(self):
        """
        Test DivideInNeighborhoods combined with FindCenterCoordinates for grid that misses one point
        and contains cosmic ray
        """
        grid_data = hdf5.read_data("grid_cosmic_ray.h5")
        C, T, Z, Y, X = grid_data[0].shape
        grid_data[0].shape = Y, X

        # Add Gaussian noise
        noise = random.normal(0, 40, grid_data[0].size)
        noise_array = noise.reshape(grid_data[0].shape[0], grid_data[0].shape[1])
        noisy_grid_data = grid_data[0] + noise_array

        subimages, subimage_coordinates, subimage_size = coordinates.DivideInNeighborhoods(noisy_grid_data, (10, 10))

        spot_coordinates = coordinates.FindCenterCoordinates(subimages)
        optical_coordinates = coordinates.ReconstructImage(subimage_coordinates, spot_coordinates, subimage_size)

        self.assertEqual(subimages.__len__(), 99)

    @unittest.skip("skip")
    def test_devide_and_find_center_grid_noise_missing_point_cosmic_ray(self):
        """
        Test DivideInNeighborhoods combined with FindCenterCoordinates for noisy input that
        misses one point and contains cosmic ray
        """
        grid_data = hdf5.read_data("grid_cosmic_ray.h5")
        C, T, Z, Y, X = grid_data[0].shape
        grid_data[0].shape = Y, X

        # Add Gaussian noise
        noise = random.normal(0, 40, grid_data[0].size)
        noise_array = noise.reshape(grid_data[0].shape[0], grid_data[0].shape[1])
        noisy_grid_data = grid_data[0] + noise_array

        subimages, subimage_coordinates, subimage_size = coordinates.DivideInNeighborhoods(noisy_grid_data, (10, 10))

        spot_coordinates = coordinates.FindCenterCoordinates(subimages)
        optical_coordinates = coordinates.ReconstructImage(subimage_coordinates, spot_coordinates, subimage_size)

        self.assertEqual(subimages.__len__(), 99)

    @unittest.skip("skip")
    def test_match_coordinates_simple(self):
        """
        Test MatchCoordinates using noisy and shuffled optical coordinates
        """
        """
        optical_coordinates = [(4.8241, 3.2631), (5.7418, 4.5738), (5.2170, 1.0348), (8.8879, 6.2774)]
        electron_coordinates = [(0, 1), (0, 2), (1, 0), (1, 4)]
        """
        """
        electron_coordinates = [ (1, 1), (1, 2), (2, 1), (2, 2)]
        optical_coordinates = []
        shuffled_coordinates = []
        for ta in electron_coordinates:
            noise_x, noise_y = gauss(0, 0.05), gauss(0, 0.05)
            optical_tuple = tuple(map(operator.add, ta, (noise_x, noise_y)))
            optical_coordinates.append(optical_tuple)
            shuffled_coordinates.append(optical_tuple)
        shuffle(shuffled_coordinates)
        print optical_coordinates
        print shuffled_coordinates

        estimated_coordinates = coordinates.MatchCoordinates(shuffled_coordinates, electron_coordinates)
        numpy.testing.assert_allclose(estimated_coordinates, shuffled_coordinates, rtol=1e-01)
        """
        # transformed_coordinates = []
        # shift_threshold = 0.1
        # print coordinates._MatchAndCalculate(shuffled_coordinates, shuffled_coordinates, electron_coordinates)


    def test_match_coordinates_precomputed_output(self):
        """
        Test MatchCoordinates for precomputed output
        """
        optical_coordinates = [(9.1243, 6.7570), (10.7472, 16.8185), (4.7271, 12.6429), (13.9714, 6.0185), (5.6263, 17.5885), (14.8142, 10.9271), (10.0384, 11.8815), (15.5146, 16.0694), (4.4803, 7.5966)]
        electron_coordinates = [(1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3), (3, 1), (3, 2), (3, 3)]

        estimated_coordinates = coordinates.MatchCoordinates(optical_coordinates, electron_coordinates)
        numpy.testing.assert_equal(estimated_coordinates, [(3, 3), (1, 3), (2, 2), (1, 1), (3, 1), (1, 2), (2, 1), (2, 3), (3, 2)])
        
    @unittest.skip("skip")
    def test_match_coordinates_single_element(self):
        """
        Test MatchCoordinates for single element lists, warning should be thrown
        """
        optical_coordinates = [(9.1243, 6.7570)]
        electron_coordinates = [(1, 1)]

        estimated_coordinates = coordinates.MatchCoordinates(optical_coordinates, electron_coordinates)
        numpy.testing.assert_equal(estimated_coordinates, [])


    def test_match_coordinates_precomputed_transformation(self):
        """
        Test MatchCoordinates for applied transformation
        """
        electron_coordinates = [(1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3), (3, 1), (3, 2), (3, 3)]

        transformed_coordinates = coordinates._TransformCoordinates(electron_coordinates, (1.0305, 2.2383), -0.4517, 0.2125)
        print transformed_coordinates

        estimated_coordinates = coordinates.MatchCoordinates(transformed_coordinates, electron_coordinates)
        numpy.testing.assert_equal(estimated_coordinates, electron_coordinates)
        (translation_x, translation_y), scaling, rotation = transform.CalculateTransform(transformed_coordinates, electron_coordinates)
        numpy.testing.assert_almost_equal((translation_x, translation_y, scaling, rotation), (1.0305, 2.2383, 0.2125, -0.4517))
        # numpy.testing.assert_equal(estimated_coordinates, [])
        print estimated_coordinates




