# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the OpenColorIO Project.

import unittest
import os
import sys

import PyOpenColorIO as OCIO
from UnitTestUtils import generate_name, get_test_file_dir, SIMPLE_CDL


class CDLTransformTest(unittest.TestCase):
    DEFAULT_SLOPE = [1.0, 1.0, 1.0]
    DEFAULT_OFFSET = [0.0, 0.0, 0.0]
    DEFAULT_POWER = [1.0, 1.0, 1.0]
    DEFAULT_SAT = 1.0

    TEST_CDL = OCIO.CDLTransform()
    TEST_CDL_ID = 'abcd'
    TEST_CDL_DESC = 'abcdefg'
    TEST_CDL_SLOPE = [1.5, 2.0, 2.5]
    TEST_CDL_OFFSET = [3.0, 3.5, 4.0]
    TEST_CDL_POWER = [4.5, 5.0, 5.5]
    TEST_CDL_SAT = 6.0

    def setUp(self):
        self.cdl = OCIO.CDLTransform()

    def tearDown(self):
        self.cdl = None

    def test_id(self):
        """
        Test the setID() and getID() methods.
        """

        id = self.cdl.getID()
        self.assertEqual(id, '')
        self.cdl.setID(CDLTransformTest.TEST_CDL_ID)
        self.assertEqual(self.cdl.getID(), CDLTransformTest.TEST_CDL_ID)
        self.cdl.validate()

        # Setup CDLTransformTest.TEST_CDL
        CDLTransformTest.TEST_CDL.setID(CDLTransformTest.TEST_CDL_ID)

        # Random string tests
        for i in range(1, 10):
            id = generate_name(20)
            self.cdl.setID(id)
            self.assertEqual(id, self.cdl.getID())
            self.cdl.validate()

    def test_description(self):
        """
        Test the setDescription() and getDescription() methods.
        """

        description = self.cdl.getDescription()
        self.assertEqual(description, '')
        self.cdl.setDescription(CDLTransformTest.TEST_CDL_DESC)
        self.assertEqual(self.cdl.getDescription(),
                         CDLTransformTest.TEST_CDL_DESC)
        self.cdl.validate()

        # Setup CDLTransformTest.TEST_CDL
        CDLTransformTest.TEST_CDL.setDescription(
            CDLTransformTest.TEST_CDL_DESC)

        # Random string tests
        for i in range(1, 10):
            desc = generate_name(20)
            self.cdl.setDescription(desc)
            self.assertEqual(desc, self.cdl.getDescription())
            self.cdl.validate()

    def test_slope(self):
        """
        Test the setSlope() and getSlope() methods.
        """

        # Default initialized slope values are [1.0, 1.0, 1.0]
        slope = self.cdl.getSlope()
        self.assertEqual(len(slope), 3)
        self.assertListEqual(CDLTransformTest.DEFAULT_SLOPE, slope)

        # Test by setting slope values to [1.5, 2.0, 2.5]
        self.cdl.setSlope(CDLTransformTest.TEST_CDL_SLOPE)
        slope = self.cdl.getSlope()
        self.assertEqual(len(slope), 3)
        self.assertListEqual(CDLTransformTest.TEST_CDL_SLOPE, slope)
        self.cdl.validate()

        # Exception validation test
        self.cdl.setSlope([-1, -2, -3])
        with self.assertRaises(OCIO.Exception):
            self.cdl.validate()

        # Setup CDLTransformTest.TEST_CDL
        CDLTransformTest.TEST_CDL.setSlope(CDLTransformTest.TEST_CDL_SLOPE)

    def test_offset(self):
        """
        Test the setOffset() and getOffset() methods.
        """

        # Default initialized offset values are [0.0, 0.0, 0.0]
        offset = self.cdl.getOffset()
        self.assertEqual(len(offset), 3)
        self.assertListEqual(CDLTransformTest.DEFAULT_OFFSET, offset)

        # Test by setting offset values to [3.0, 3.5, 4.0]
        self.cdl.setOffset(CDLTransformTest.TEST_CDL_OFFSET)
        offset = self.cdl.getOffset()
        self.assertEqual(len(offset), 3)
        self.assertListEqual(CDLTransformTest.TEST_CDL_OFFSET, offset)
        self.cdl.validate()

        # Setup CDLTransformTest.TEST_CDL
        CDLTransformTest.TEST_CDL.setOffset(CDLTransformTest.TEST_CDL_OFFSET)

    def test_power(self):
        """
        Test the setPower() and getPower() methods.
        """

        # Default initialized power values are [0.0, 0.0, 0.0]
        power = self.cdl.getPower()
        self.assertEqual(len(power), 3)
        self.assertListEqual(CDLTransformTest.DEFAULT_POWER, power)

        # Test by setting power values to [4.5, 5.0, 5.5]
        self.cdl.setPower(CDLTransformTest.TEST_CDL_POWER)
        power = self.cdl.getPower()
        self.assertEqual(len(power), 3)
        self.assertListEqual(CDLTransformTest.TEST_CDL_POWER, power)
        self.cdl.validate()

        # Exception validation test
        self.cdl.setPower([-1, -2, -3])
        with self.assertRaises(OCIO.Exception):
            self.cdl.validate()

        # Setup CDLTransformTest.TEST_CDL
        CDLTransformTest.TEST_CDL.setPower(CDLTransformTest.TEST_CDL_POWER)

    def test_saturation(self):
        """
        Test the setSat() and getSat() methods.
        """

        # Default initialized saturation value is 1.0
        saturation = self.cdl.getSat()
        self.assertEqual(CDLTransformTest.DEFAULT_SAT, saturation)

        # Test by setting saturation value to 6.0
        self.cdl.setSat(CDLTransformTest.TEST_CDL_SAT)
        self.assertEqual(self.cdl.getSat(), CDLTransformTest.TEST_CDL_SAT)
        self.cdl.validate()

        # Exception validation test
        self.cdl.setSat(-1)
        with self.assertRaises(OCIO.Exception):
            self.cdl.validate()

        # Setup CDLTransformTest.TEST_CDL
        CDLTransformTest.TEST_CDL.setSat(CDLTransformTest.TEST_CDL_SAT)

    def test_direction(self):
        """
        Test the setDirection() and getDirection() methods.
        """

        # Default initialized direction is forward.
        self.assertEqual(self.cdl.getDirection(), OCIO.TRANSFORM_DIR_FORWARD)

        for direction in OCIO.TransformDirection.__members__.values():
            self.cdl.setDirection(direction)
            self.assertEqual(self.cdl.getDirection(), direction)
            self.cdl.validate()

    def test_style(self):
        # Default initialized direction is forward.
        self.assertEqual(self.cdl.getStyle(), OCIO.CDL_ASC)

        for style in OCIO.CDLStyle.__members__.values():
            self.cdl.setStyle(style)
            self.assertEqual(self.cdl.getStyle(), style)
            self.cdl.validate()

    def test_xml(self):
        """
        Test the setXML() and getXML() methods.
        """

        xml = CDLTransformTest.TEST_CDL.getXML()
        cdl = CDLTransformTest.TEST_CDL
        self.assertEqual(cdl.getID(), CDLTransformTest.TEST_CDL_ID)
        self.assertEqual(cdl.getDescription(), CDLTransformTest.TEST_CDL_DESC)
        self.assertListEqual(cdl.getSlope(), CDLTransformTest.TEST_CDL_SLOPE)
        self.assertListEqual(cdl.getOffset(), CDLTransformTest.TEST_CDL_OFFSET)
        self.assertListEqual(cdl.getPower(), CDLTransformTest.TEST_CDL_POWER)
        self.assertEqual(cdl.getSat(), CDLTransformTest.TEST_CDL_SAT)

        self.cdl.setXML(SIMPLE_CDL)
        self.assertEqual(self.cdl.getID(), 'shot 042')
        self.assertEqual(self.cdl.getDescription(),
                         'Cool look for forest scenes')
        self.assertListEqual(self.cdl.getSlope(), [1.0, 2.0, 3.0])
        self.assertListEqual(self.cdl.getOffset(), [4.0, 5.0, 6.0])
        self.assertListEqual(self.cdl.getPower(), [7.0, 8.0, 9.0])
        self.assertEqual(self.cdl.getSat(), 10.0)

    def test_createfromfile(self):
        """
        Test CreateFromFile() method.
        """

        # Try env var first to get test file path or use ./tests/data/files/*
        test_file = '%s/cdl_test1.ccc' % get_test_file_dir()

        # Test 4th member of the ccc file.
        cdl1 = self.cdl.CreateFromFile(test_file, "3")
        self.assertEqual(cdl1.getID(), '')
        self.assertListEqual(cdl1.getSlope(), [4.0, 5.0, 6.0])
        self.assertListEqual(cdl1.getOffset(), [0.0, 0.0, 0.0])
        self.assertListEqual(cdl1.getPower(), [0.9, 1.0, 1.2])
        self.assertEqual(cdl1.getSat(), 1.0)

        # Test a specified id member of the ccc file.
        cdl2 = self.cdl.CreateFromFile(test_file, "cc0003")
        self.assertEqual(cdl2.getID(), 'cc0003')
        self.assertEqual(cdl2.getDescription(), 'golden')
        self.assertListEqual(cdl2.getSlope(), [1.2, 1.1, 1.0])
        self.assertListEqual(cdl2.getOffset(), [0.0, 0.0, 0.0])
        self.assertListEqual(cdl2.getPower(), [0.9, 1.0, 1.2])
        self.assertEqual(cdl2.getSat(), 1.0)

    def test_equality(self):
        """
        Test the equals() method.
        """

        cdl1 = OCIO.CDLTransform()
        self.assertTrue(cdl1.equals(cdl1))

        cdl2 = OCIO.CDLTransform()
        self.assertTrue(cdl1.equals(cdl2))
        self.assertTrue(cdl2.equals(cdl1))

        cdl1.setSat(0.12601234)
        self.assertFalse(cdl1.equals(cdl2))
        self.assertFalse(cdl2.equals(cdl1))

        cdl2.setSat(0.12601234)
        self.assertTrue(cdl1.equals(cdl2))
        self.assertTrue(cdl2.equals(cdl1))

    def test_z_equality(self):
        """
        Test the equals() method with the TEST_CDL.
        """

        self.cdl.setSlope(CDLTransformTest.TEST_CDL_SLOPE)
        self.cdl.setOffset(CDLTransformTest.TEST_CDL_OFFSET)
        self.cdl.setPower(CDLTransformTest.TEST_CDL_POWER)
        self.cdl.setSat(CDLTransformTest.TEST_CDL_SAT)
        test_cdl = CDLTransformTest.TEST_CDL
        self.assertTrue(test_cdl.equals(self.cdl))
