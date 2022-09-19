import sys
sys.path.append("..")
from src.char_data_maker import CharDataMaker 
CG = CharDataMaker("/Users/jkerxhallikl/Desktop/RexPaintImageImporter/cp437_20x20.png", 20, "/Users/jkerxhallikl/Desktop/RexPaintImageImporter/_utf8.txt")
print(CG.generate_image_meta())