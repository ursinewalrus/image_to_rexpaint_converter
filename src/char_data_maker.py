import PIL
from functools import reduce
from src.lib.types import *
from typing import List, Dict
import json
from src.lib.image_traversal_utils import * 
import os

class CharDataMaker:

	def __init__(self, image_path : str, chunk_size : int, character_map_path : str):
		self.image: Image = PIL.Image.open(image_path)
		self.chunk_size: int = chunk_size
		self.character_map: str = character_map_path
		self.image_meta = []

		self.image_file_name = os.path.basename(image_path)
		self.character_map_file_name = os.path.basename(character_map_path)

	def generate_image_meta(self):
		im_w, im_y = self.image.size[0], self.image.size[1]
		
		cropped_w: int = im_w - (im_w % self.chunk_size)
		cropped_y: int= im_y - (im_y % self.chunk_size)

		self.image = self.image.crop((0,0,cropped_w, cropped_y))

		char_chunk_data: List[List[CharSubRegionData]] = image_chunk_meta_mapper(generate_character_sub_region_data, self.image, self.chunk_size)

		lexical_reps: List[CharData] = list(map(char_string_representation_reducer, char_chunk_data))
		lexical_reps_with_charcodes =  self.__zip_char_codes_into_chunk_data(lexical_reps)

		with open(f"{self.image_file_name}_{self.character_map_file_name}_mapping.json", "w") as f:
			f.write(json.dumps(lexical_reps_with_charcodes))

	def __zip_char_codes_into_chunk_data(self, char_data: List[CharData]) -> Dict[str, Dict[str, int] ]:
		zipper = lambda dict_key, data, codes: dict(zip(map(lambda char: char[dict_key],data), codes))
		packaged_vals = {}
		with open(self.character_map, 'r') as f:
			lines = f.readlines()
			char_codes = [int(l.strip().split(" ")[1]) for l in lines]
			packaged_vals["simple_char_gradient_str"] = zipper("simple_char_gradient_str", char_data, char_codes)
			packaged_vals["granular_char_gradient_str"] = zipper("granular_char_gradient_str", char_data, char_codes)

		return packaged_vals

