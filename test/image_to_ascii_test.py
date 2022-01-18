import sys
import cProfile
sys.path.append("..")
from src.image_to_ascii import ImageToAscii

ItA = ImageToAscii("../me.jpg", "./cp437_20x20.png__utf8.txt_mapping.json", 3, "simple_char_gradient_str", True)

ItANoCache = ImageToAscii("../me.jpg", "./cp437_20x20.png__utf8.txt_mapping.json", 3,  "simple_char_gradient_str", False)

cProfile.run('ItA.convert_image_to_ascii()')
print("___")
cProfile.run('ItANoCache.convert_image_to_ascii()')


