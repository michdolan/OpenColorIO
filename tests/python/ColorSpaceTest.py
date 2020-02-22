# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the OpenColorIO Project.

import unittest
import os
import sys
from random import randint
import PyOpenColorIO as OCIO
from Constants import ACES_1_1_CONFIG


def generate_name(digits):
    """
    Randomly generate ASCII value 32 to 126 upto specified digit amount.
    https://www.asciichart.com

    :param digits: Number of digits in the name.
    :type digits: int
    :return: Randomly generated alphanumeric string.
    :rtype: str
    """

    name = ''
    for x in range(0, randint(1, digits)):
        name += chr(randint(32, 127))
    return name


class ColorSpaceTest(unittest.TestCase):
    def setUp(self):
        """
        Set up self.cs as OCIO.ColorSpace and OCIO.LogTransform objects.
        """

        self.cs = OCIO.ColorSpace()
        self.lt = OCIO.LogTransform()

    def tearDown(self):
        """
        Clear the self.cs variable.
        """

        self.cs = None
        self.lt = None

    def test_editable(self):
        """
        Test the isEditable() and createEditableCopy() methods.
        """

        # Basic test
        self.assertTrue(self.cs.isEditable())

        # Getter check
        transform_base = 10
        self.lt.setBase(transform_base)
        self.cs.setTransform(self.lt, OCIO.COLORSPACE_DIR_TO_REFERENCE)
        ott = self.cs.getTransform(OCIO.COLORSPACE_DIR_TO_REFERENCE)
        self.assertFalse(ott.isEditable())
        with self.assertRaises(OCIO.Exception):
            ott.setBase(20)

        cs_copy = self.cs.createEditableCopy()
        self.assertTrue(cs_copy.isEditable())
        self.assertIsInstance(cs_copy, OCIO.ColorSpace)
        self.assertIsNot(cs_copy, self.cs)

    def test_name(self):
        """
        Test the setName() and getName() methods.
        """

        # Basic test
        self.cs.setName("mynewcolspace")
        self.assertEqual("mynewcolspace", self.cs.getName())

        # Random string tests
        for i in range(1, 10):
            name = generate_name(10)
            self.cs.setName(name)
            self.assertEqual(name, self.cs.getName())

    def test_family(self):
        """
        Test the setFamily() and getFamily() methods.
        """

        # Basic test
        self.cs.setFamily("fam1")
        self.assertEqual("fam1", self.cs.getFamily())

        # Random string tests
        for i in range(1, 10):
            name = generate_name(10)
            self.cs.setFamily(name)
            self.assertEqual(name, self.cs.getFamily())

    def test_equality(self):
        """
        Test the setEqualityGroup() and getEqualityGroup() methods.
        """

        # Basic test
        self.cs.setEqualityGroup("match1")
        self.assertEqual("match1", self.cs.getEqualityGroup())

        # Random string tests
        for i in range(1, 10):
            name = generate_name(10)
            self.cs.setEqualityGroup(name)
            self.assertEqual(name, self.cs.getEqualityGroup())

    def test_description(self):
        """
        Test the setDescription() and getDescription() methods.
        """

        # Basic test
        self.cs.setDescription("this is a test")
        self.assertEqual("this is a test", self.cs.getDescription())

        # Random string tests
        for i in range(1, 10):
            name = generate_name(20)
            self.cs.setDescription(name)
            self.assertEqual(name, self.cs.getDescription())

    def test_bitdepth(self):
        """
        Test the setBitDepth() and getBitDepth() methods.
        """

        # Known constants tests
        for bit_depth in range(9):
            self.cs.setBitDepth(OCIO.BitDepth(bit_depth))
            self.assertEqual(OCIO.BitDepth(bit_depth), self.cs.getBitDepth())

        # Random string tests
        for i in range(0, 10):
            name = generate_name(10)
            with self.assertRaises(TypeError):
                self.cs.setBitDepth(name)

        # Wrong type tests
        with self.assertRaises(TypeError):
            self.cs.setBitDepth(None)

    def test_data(self):
        """
        Test the setIsData() and getIsData() methods.
        """

        # Boolean tests
        is_datas = [True, False]
        for is_data in is_datas:
            self.cs.setIsData(is_data)
            self.assertEqual(is_data, self.cs.isData())

        # Wrong type tests
        wrong_is_datas = [['test'],
                          'test']
        for wrong_is_data in wrong_is_datas:
            with self.assertRaises(TypeError):
                self.cs.setIsData(wrong_is_data)

    def test_allocation(self):
        """
        Test the setAllocation() and getAllocation() methods.
        """

        # Known constants tests
        for allocation in range(3):
            self.cs.setAllocation(OCIO.Allocation(allocation))
            self.assertEqual(allocation, self.cs.getAllocation())

        # Random string tests
        for i in range(0, 10):
            name = generate_name(10)
            with self.assertRaises(TypeError):
                self.cs.setAllocation(name)

        # Wrong type tests
        with self.assertRaises(TypeError):
            self.cs.setAllocation(None)

    def test_allocation_vars(self):
        """
        Test the setAllocationVars() and getAllocationVars() methods.
        """

        # Array length tests
        alloc_var = []
        for i in range(1, 4):
            # This will create [0.1], [0.1, 0.2] and finally [0.1, 0.2, 0.3]
            alloc_var.append(float('0.%i' % i))
            if i == 1:
                with self.assertRaises(OCIO.Exception):
                    self.cs.setAllocationVars(alloc_var)
            else:
                self.cs.setAllocationVars(alloc_var)
                self.assertEqual(len(alloc_var), len(
                    self.cs.getAllocationVars()))

        # Wrong type tests
        wrong_alloc_vars = [['test'],
                            'test',
                            0.1,
                            1]
        for wrong_alloc_var in wrong_alloc_vars:
            with self.assertRaises(TypeError):
                self.cs.setAllocationVars(wrong_alloc_var)

    def test_transform(self):
        """
        Test the setTransform() and getTransform() methods.
        """

        transform_base = 10
        self.lt.setBase(transform_base)

        # Known constants tests
        for direction in range(3):
            direction_obj = OCIO.ColorSpaceDirection(direction)
            if direction_obj == OCIO.COLORSPACE_DIR_UNKNOWN:
                with self.assertRaises(OCIO.Exception):
                    self.cs.setTransform(self.lt, direction_obj)
            else:
                self.cs.setTransform(self.lt, direction_obj)

            if direction_obj == OCIO.COLORSPACE_DIR_UNKNOWN:
                with self.assertRaises(OCIO.Exception):
                    ott = self.cs.getTransform(
                        direction_obj)
            else:
                ott = self.cs.getTransform(direction_obj)
                self.assertFalse(ott.isEditable())
                self.assertIsInstance(ott, OCIO.LogTransform)
                self.assertEquals(transform_base, ott.getBase())

    def test_config(self):
        """
        Test the ColorSpace object from an OCIO config.
        """

        # Get ACES 1.1 config file from Constants.py
        cfg = OCIO.Config().CreateFromStream(ACES_1_1_CONFIG)
        self.assertFalse(cfg.isEditable())

        # Test ColorSpace class object getters
        cs = cfg.getColorSpace('ACES - ACEScg')
        self.assertFalse(cs.isEditable())
        self.assertEqual(cs.getName(), 'ACES - ACEScg')
        self.assertEqual(cs.getDescription(),
                         'The ACEScg color space\n\nACES Transform ID : ACEScsc.ACEScg_to_ACES\n')
        self.assertEqual(cs.getFamily(), 'ACES')
        self.assertEqual(cs.getAllocation(), OCIO.ALLOCATION_LG2)
        self.assertEqual(cs.getAllocationVars(), [-8, 5, 0.00390625])
        self.assertEqual(cs.getEqualityGroup(), "")
        self.assertEqual(cs.getBitDepth(), OCIO.BIT_DEPTH_F32)
        self.assertFalse(cs.isData())
        for direction in [OCIO.COLORSPACE_DIR_TO_REFERENCE,
                          OCIO.COLORSPACE_DIR_FROM_REFERENCE]:
            mt = cs.getTransform(direction)
            self.assertIsInstance(mt, OCIO.MatrixTransform)
            self.assertFalse(mt.isEditable())
        with self.assertRaises(OCIO.Exception):
            mt = cs.getTransform(OCIO.COLORSPACE_DIR_UNKNOWN)
