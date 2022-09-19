import os
import string
from typing import List

import PIL
import pytest
from PIL import Image

from src.lib.types import ProcessedImageChunkData, ConvertedPackagedImageData
from src.lib.xp_file_maker import XPFileMaker

fixture_location = "src/test/on_disc_fixtures/"
default_mappings = f"{fixture_location}default_mappings.json"
from src.image_to_ascii import ImageToAscii




@pytest.fixture
def three_x_three_red_image() -> string:
    file_location = f"{fixture_location}3x3_red_px.png"
    im = PIL.Image.new(mode="RGB", size=(3, 3), color=(255, 0, 0))
    im.save(file_location, format="PNG")
    im = Image.open(file_location)
    return im.filename

@pytest.fixture
def xp_file_maker_with_image(three_x_three_red_image) -> XPFileMaker:
    im_to_ascii = ImageToAscii(three_x_three_red_image, default_mappings, 3)
    image_as_json: ConvertedPackagedImageData = im_to_ascii.convert_and_package_for_export()
    return XPFileMaker(image_as_json)

def test_binary_output(xp_file_maker_with_image):
    # check its in there
    assert len(xp_file_maker_with_image.image_data) == 1
    assert xp_file_maker_with_image.image_data[0].foreground_color == (255, 0, 0)
    assert xp_file_maker_with_image.row_len == 1
    # don't check char code that could be highly variable even for such a simple case
    generated_binary = xp_file_maker_with_image.construct_xp_file_binary()
    # assert False


    expected_binary = ("11111111111111111111111111111111" +  # version
    "00000001000000000000000000000000" + # 1 layer little endian
    "00000001000000000000000000000000" + # 1 width little endian
    "00000001000000000000000000000000" + # 1 height little endian
    "10010001000000000000000000100101" + # char little endian
    "11111111" + # red forground
    "00000000" + # green forground
    "00000000" + # blue forground
    "00000000" +
    "00000000" + 
    "00000000") 
    assert expected_binary[:32] == generated_binary[:32] #version written right
    assert expected_binary[32:64] == generated_binary[32:64] #layers written right
    assert expected_binary[64:96] == generated_binary[64:96] #width written right
    assert expected_binary[96:128] == generated_binary[96:128] #height written right
    assert expected_binary[128:160] == generated_binary[128:160] #char written right
    assert expected_binary[160:168] == generated_binary[160:168] #red fore written right
    assert expected_binary[168:176] == generated_binary[168:176] #red fore written right
    assert expected_binary[176:184] == generated_binary[176:184] #red fore written right
    assert generated_binary == expected_binary