import sys
from image_to_ascii import ImageToAscii


# assumes and image wa passed in via task and is sitting in  /images/image.jpg
from lib.types import ConvertedPackagedImageData
from lib.xp_file_maker import XPFileMaker
print(sys.argv)
image_name = sys.argv[1]
scaling = int(sys.argv[2])

ItA = ImageToAscii(f"/images/{image_name}", "/rexpaint/src/mapping_tools/cp437_20x20.png__utf8.txt_mapping.json", scaling, "granular_char_gradient_str", True)
image_as_json: ConvertedPackagedImageData = ItA.convert_and_package_for_export()

xpFileMaker = XPFileMaker(image_as_json, image_name.split(".")[0])
print(xpFileMaker.construct_xp_file_binary())
ItA.print_ascii_output()

