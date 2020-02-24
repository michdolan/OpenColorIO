# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the OpenColorIO Project.

import unittest
import os
import sys
from random import randint
import PyOpenColorIO as OCIO
from Constants import SIMPLE_CONFIG


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
            name = generate_name(20)
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
            name = generate_name(20)
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
            name = generate_name(20)
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
        for i, bit_depth in enumerate(OCIO.BitDepth.__members__.values()):
            self.assertEqual(bit_depth.name, OCIO.BitDepth(i).name)
            self.cs.setBitDepth(bit_depth)
            self.assertEqual(OCIO.BitDepth(bit_depth), self.cs.getBitDepth())

        # Wrong type tests
        for i in range(0, 10):
            name = generate_name(20)
            with self.assertRaises(TypeError):
                self.cs.setBitDepth(name)
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
        for i, allocation in enumerate(OCIO.Allocation.__members__.values()):
            self.assertEqual(allocation.name, OCIO.Allocation(i).name)
            self.cs.setAllocation(allocation)
            self.assertEqual(allocation, self.cs.getAllocation())

        # Wrong type tests
        for i in range(0, 10):
            name = generate_name(20)
            with self.assertRaises(TypeError):
                self.cs.setAllocation(name)
        with self.assertRaises(TypeError):
            self.cs.setAllocation(None)

    def test_allocation_vars(self):
        """
        Test the setAllocationVars() and getAllocationVars() methods.
        """

        # Array length tests
        alloc_var = []
        for i in range(1, 5):
            # This will create [0.1] up to [0.1, 0.2, 0.3, 0.4]
            alloc_var.append(float('0.%i' % i))
            if i < 2 or i > 3:
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
        for i, direction in enumerate(
                OCIO.ColorSpaceDirection.__members__.values()):
            self.assertEqual(direction.name, OCIO.ColorSpaceDirection(i).name)
            if direction == OCIO.COLORSPACE_DIR_UNKNOWN:
                with self.assertRaises(OCIO.Exception):
                    self.cs.setTransform(self.lt, direction)
            else:
                self.cs.setTransform(self.lt, direction)

            if direction == OCIO.COLORSPACE_DIR_UNKNOWN:
                with self.assertRaises(OCIO.Exception):
                    ott = self.cs.getTransform(
                        direction)
            else:
                ott = self.cs.getTransform(direction)
                self.assertFalse(ott.isEditable())
                self.assertIsInstance(ott, OCIO.LogTransform)
                self.assertEquals(transform_base, ott.getBase())

    def test_category(self):
        """
        Test the hasCategory(), addCategory(), removeCategory(),
        getCategories() and clearCategories() methods.
        """

        # Test empty categories
        self.assertFalse(self.cs.hasCategory('ocio'))
        self.assertEqual(len(self.cs.getCategories()), 0)
        with self.assertRaises(IndexError):
            self.cs.getCategories()[0]

        # Test with categories with defined and random string
        categories = ['render', 'input', 'ocio', 'test']
        for _ in range(4):
            categories.append(generate_name(20))

        for y in categories:
            self.cs.addCategory(y)
            self.assertTrue(self.cs.hasCategory(y))

        for j, i in enumerate(self.cs.getCategories()):
            self.assertEqual(i, categories[j])

        self.assertEqual(len(self.cs.getCategories()), 8)

        iterator = self.cs.getCategories()
        for a in categories:
            self.assertEqual(a, next(iterator))
        self.cs.clearCategories()
        self.assertEqual(len(self.cs.getCategories()), 0)

        for y in categories:
            self.assertEqual(len(self.cs.getCategories()), 0)
            self.cs.addCategory(y)
            self.assertEqual(len(self.cs.getCategories()), 1)
            self.cs.removeCategory(y)
        self.assertEqual(len(self.cs.getCategories()), 0)

    def test_config(self):
        """
        Test the ColorSpace object from an OCIO config.
        """

        # Get ACES 1.1 config file from Constants.py
        cfg = OCIO.Config().CreateFromStream(SIMPLE_CONFIG)
        self.assertFalse(cfg.isEditable())

        # Test ColorSpace class object getters from config
        cs = cfg.getColorSpace('vd8')
        self.assertFalse(cs.isEditable())
        self.assertEqual(cs.getName(), 'vd8')
        self.assertEqual(cs.getDescription(),
                         'how many transforms can we use?\n')
        self.assertEqual(cs.getFamily(), 'vd8')
        self.assertEqual(cs.getAllocation(), OCIO.ALLOCATION_UNIFORM)
        self.assertEqual(cs.getAllocationVars(), [])
        self.assertEqual(cs.getEqualityGroup(), '')
        self.assertEqual(cs.getBitDepth(), OCIO.BIT_DEPTH_UINT8)
        self.assertFalse(cs.isData())

        to_ref = cs.getTransform(OCIO.COLORSPACE_DIR_TO_REFERENCE)
        transforms = to_ref.getTransforms()
        self.assertIsInstance(transforms, OCIO.GroupTransform)
        self.assertEqual(len(transforms), 3)

        exp_transform = transforms[0]
        self.assertFalse(exp_transform.isEditable())
        self.assertIsInstance(exp_transform, OCIO.ExponentTransform)
        self.assertEqual(exp_transform.getValue(), [2.2, 2.2, 2.2, 1])

        matrix_transform = transforms[1]
        self.assertFalse(matrix_transform.isEditable())
        self.assertIsInstance(matrix_transform, OCIO.MatrixTransform)
        self.assertEqual(matrix_transform.getMatrix(),
                         [1, 2, 3, 4, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1])
        self.assertEqual(matrix_transform.getOffset(), [1, 2, 0, 0])

        cdl_transform = transforms[2]
        self.assertFalse(cdl_transform.isEditable())
        self.assertIsInstance(cdl_transform, OCIO.CDLTransform)
        self.assertEqual(cdl_transform.getSlope(), [0.9, 1, 1])
        self.assertEqual(cdl_transform.getOffset(), [0.1, 0.3, 0.4])
        self.assertEqual(cdl_transform.getPower(), [1.1, 1.1, 1.1])
        self.assertEqual(cdl_transform.getSat(), 0.9)

    def test_constructor(self):
        """
        Test ColorSpace constructor and validate its values.
        """

        cs = OCIO.ColorSpace(name='test',
                             family='ocio',
                             equalityGroup='input',
                             bitDepth=OCIO.BIT_DEPTH_F32,
                             description='This is a test colourspace!',
                             isData=False,
                             allocation=OCIO.ALLOCATION_LG2,
                             allocationVars=[0.0, 1.0])

        self.assertTrue(cs.isEditable())
        self.assertEqual(cs.getName(), 'test')
        self.assertEqual(cs.getDescription(), 'This is a test colourspace!')
        self.assertEqual(cs.getFamily(), 'ocio')
        self.assertEqual(cs.getAllocation(), OCIO.ALLOCATION_LG2)
        self.assertEqual(cs.getAllocationVars(), [0.0, 1.0])
        self.assertEqual(cs.getEqualityGroup(), 'input')
        self.assertEqual(cs.getBitDepth(), OCIO.BIT_DEPTH_F32)
        self.assertFalse(cs.isData())
