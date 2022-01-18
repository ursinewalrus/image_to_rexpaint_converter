import sys
sys.path.append("..")
from src.char_data_maker import CharDataMaker 
CG = CharDataMaker("../cp437_20x20.png", 20, "../_utf8.txt")
print(CG.generate_image_meta())