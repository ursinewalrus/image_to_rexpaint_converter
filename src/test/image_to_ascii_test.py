from src.image_to_ascii import ImageToAscii
from src.lib.types import ConvertedPackagedImageData
from src.lib.xp_file_maker import XPFileMaker

ItA = ImageToAscii("/Users/jkerxhallikl/Desktop/RexPaintImageImporter/brain.jpg",
                   "/src/mapping_tools/cp437_20x20.png__utf8.txt_mapping.json", 20, "granular_char_gradient_str", True)
image_as_json: ConvertedPackagedImageData =  ItA.convert_and_package_for_export()

xpFileMaker = XPFileMaker(image_as_json)
print(xpFileMaker.construct_xp_file_binary())
ItA.print_ascii_output()


