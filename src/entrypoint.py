import os
import sys
from image_to_ascii import ImageToAscii


from lib.types import ConvertedPackagedImageData, ImageGranularity
from lib.xp_file_maker import XPFileMaker
scaling = int(sys.argv[1])
granularity = sys.argv[2]
bw = sys.argv[3]

if granularity == "G":
    granularity = ImageGranularity.GRANULAR
else:
    granularity = ImageGranularity.SIMPLE

if bw == "y" or bw == "Y":
    bw = True
else:
    bw = False

for image_name in os.listdir("./inputs/"):
    print("COLOR BW :", bw)
    print("converting ", image_name)
    if os.path.isfile(os.path.join("./inputs/", image_name)):
        print("converting", image_name )
        ItA = ImageToAscii(f"inputs/{image_name}",
                           "/rexpaint/src/mapping_tools/cp437_20x20.png__utf8.txt_mapping.json",
                           reduce_ratio=scaling,
                           granularity=granularity,
                           black_and_white=bw)
        image_as_json: ConvertedPackagedImageData = ItA.convert_and_package_for_export()

        xpFileMaker = XPFileMaker(image_as_json, image_name.split(".")[0])
        # print(xpFileMaker.construct_xp_file_binary())
        ItA.print_ascii_output()


# if __name__ == "__main__":

