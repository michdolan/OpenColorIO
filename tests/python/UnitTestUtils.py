import os
from random import randint


SIMPLE_CONFIG = """ocio_profile_version: 1

search_path: luts
strictparsing: false
luma: [0.2126, 0.7152, 0.0722]

roles:
  default: raw
  scene_linear: lnh

displays:
  sRGB:
    - !<View> {name: Film1D, colorspace: vd8}
    - !<View> {name: Raw, colorspace: raw}

active_displays: []
active_views: []

colorspaces:
  - !<ColorSpace>
    name: raw
    family: raw
    equalitygroup: ""
    bitdepth: 32f
    description: |
      A raw color space. Conversions to and from this space are no-ops.

    isdata: true
    allocation: uniform

  - !<ColorSpace>
    name: lnh
    family: ln
    equalitygroup: ""
    bitdepth: 16f
    description: |
      The show reference space. This is a sensor referred linear
      representation of the scene with primaries that correspond to
      scanned film. 0.18 in this space corresponds to a properly
      exposed 18% grey card.

    isdata: false
    allocation: lg2

  - !<ColorSpace>
    name: vd8
    family: vd8
    equalitygroup: ""
    bitdepth: 8ui
    description: |
      how many transforms can we use?

    isdata: false
    allocation: uniform
    to_reference: !<GroupTransform>
      children:
        - !<ExponentTransform> {value: [2.2, 2.2, 2.2, 1]}
        - !<MatrixTransform> {matrix: [1, 2, 3, 4, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1], offset: [1, 2, 0, 0]}
        - !<CDLTransform> {slope: [0.9, 1, 1], offset: [0.1, 0.3, 0.4], power: [1.1, 1.1, 1.1], sat: 0.9}
"""

SIMPLE_CDL = """
<ColorCorrection id='shot 042'>
    <SOPNode>
        <Description>Cool look for forest scenes</Description>
        <Slope>1 2 3</Slope>
        <Offset>4 5 6</Offset>
        <Power>7 8 9</Power>
    </SOPNode>
    <SatNode>
        <Saturation>10</Saturation>
    </SatNode>
</ColorCorrection>
"""


def generate_name(digits):
    """
    Randomly generate ASCII value 32 to 126 upto specified digit amount.
    First and last char will not contain space letter.
    https://www.asciichart.com

    :param digits: Number of digits in the name.
    :type digits: int
    :return: Randomly generated alphanumeric string.
    :rtype: str
    """

    name = ''
    last_digit = randint(1, digits)
    for x in range(0, last_digit):
        if x == 0 or x == last_digit - 1:
            name += chr(randint(33, 127))
        else:
            name += chr(randint(32, 127))
    return name


def get_test_file_dir():
    """
    Return the testing file directory in the following priority:
    1) $[UNITTEST_DEST_DIR]/testdata/
    2) $[CMAKE_BINARY_DIR]/tests/data/files/
    3) [Python unittest file directory]/../tests/data/files/

    :return: Test files directory.
    :rtype: str
    """

    test_file_dir = os.getenv('UNITTEST_DEST_DIR', None)
    if test_file_dir is None:
        test_file_dir = os.getenv('CMAKE_BINARY_DIR', None)
        if test_file_dir:
            test_file_dir = os.path.join(
                test_file_dir, 'tests', 'data', 'files')
        else:
            test_file_dir = os.path.join(os.path.dirname(
                os.path.dirname(__file__)), 'data', 'files')
    return test_file_dir
