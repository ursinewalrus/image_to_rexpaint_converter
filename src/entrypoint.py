import os
import sys
from image_to_ascii import ImageToAscii


from lib.types import ConvertedPackagedImageData
from lib.xp_file_maker import XPFileMaker
scaling = int(sys.argv[1])

for image_name in os.listdir("./inputs/"):
    print("checking ", image_name)
    if os.path.isfile(os.path.join("./inputs/", image_name)):
        print("converting", image_name )
        ItA = ImageToAscii(f"inputs/{image_name}", "/rexpaint/src/mapping_tools/cp437_20x20.png__utf8.txt_mapping.json", scaling, "granular_char_gradient_str", True)
        image_as_json: ConvertedPackagedImageData = ItA.convert_and_package_for_export()

        xpFileMaker = XPFileMaker(image_as_json, image_name.split(".")[0])
        print(xpFileMaker.construct_xp_file_binary())
        ItA.print_ascii_output()


# if __name__ == "__main__":

