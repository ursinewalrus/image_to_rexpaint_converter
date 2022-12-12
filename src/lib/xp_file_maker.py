"""
https://github.com/Lucide/REXPaint-manual/blob/master/manual.md#appendix-b-xp-format-specification-and-import-libraries
#─────xp format version (32) -> ignored (all 1's)

A─────number of layers (32) (little─endian!)
 ┌────image width (32) (little─endian!)
 │    image height (32) (little─endian!)
 │  ┌─ASCII code (32) (little─endian!)
B│  │ foreground color red (8)
 │  │ foreground color green (8)
 │  │ foreground color blue (8)
 │ C│ background color red (8)
 │  │ background color green (8)
 └──┴─background color blue (8)
"""
import string
from typing import List
import gzip

from src.lib.types import ConvertedPackagedImageData, ProcessedImageChunkData

# f = open("raw_binary_of_sheep.txt", "r" )
# contents = f.read()
# contents = contents.replace("\n","")
# to_write = int(contents, 2).to_bytes((len(contents) + 7) // 8, 'big')
# f1=gzip.open("sheep.xp","wb")
# f1.write(to_write)

# currently it seems to be rotating the image 90 degrees to the left and flipping it

class XPFileMaker:

    def __init__(self, json_data: ConvertedPackagedImageData, outputFile: string):
        self.image_data: List[ProcessedImageChunkData] = json_data.converted_image
        self.row_len = json_data.row_len
        self.binary_file_contents = self.construct_xp_file_binary()

        # dont remember why this works at all
        to_write = int(self.binary_file_contents, 2).to_bytes((len(self.binary_file_contents) + 7) //8, 'big')
        xp_file = gzip.open(f"/rexpaint/outputs/{outputFile}.xp", "wb")
        xp_file.write(to_write)

        # with open(f"/rexpaint/outputs/{outputFile}.xp", "w+") as f:
        #     f.write(self.binary_file_contents)

    def get_json_data(self):
        return self.image_data

    def little_endian_convert(self, num: int, byte_num: int=4) -> bytes:
        bin_version = format(num, f"0{byte_num * 8}b")
        return bin_version[-8:]+bin_version[:-8]

    def construct_xp_file_binary(self) -> string:
        binary_string = ""
        # create the 32 bit version info, just setting it to '1'
        binary_string += "1" * 32
        # layers is going to be 1 each time for now
        binary_string += self.little_endian_convert(1)
        # now width
        binary_string += self.little_endian_convert(self.row_len)
        # now height, calculate and write
        im_height = len(self.image_data) // self.row_len
        binary_string += self.little_endian_convert(im_height)

        # now we can just loop through all the chars and write them...
        for charData in self.image_data:
            charData: ProcessedImageChunkData
            # ascii code, 32 little endian - very likely wrong
            # character_code = struct.pack('<Q', charData.character)
            binary_string += self.little_endian_convert(charData.character)
            # foreground(only atm)colors - likely wrong also
            for color in charData.foreground_color:
                binary_string += format(color, "08b")
            # add background color for the chars, for now all black, 3 bytes of 0's
            binary_string += "0"*24

        return binary_string
