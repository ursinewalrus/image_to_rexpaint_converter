from typing import Dict
import PIL
import nltk
from src.lib.types import *
from src.lib.image_traversal_utils import * 
import json
import random
# https://stackoverflow.com/questions/55487618/looking-for-python-library-which-can-perform-levenshtein-other-edit-distance-at
class ImageToAscii:

    def __init__(self, image_path: str, char_map_filepath: str, reduce_ratio: int, granularity: str="simple_char_gradient_str", use_cache: bool = True):
        self.image: Image = PIL.Image.open(image_path)
        # with open(char_map_filepath) as map_data:
        #     self.map_data = json.load(map_data)
        with open(char_map_filepath) as f:
            self.char_map = json.load(f)
        # must be at least 3
        if reduce_ratio < 3:
            reduce_ratio = 3
        self.reduce_ratio: int = reduce_ratio

        if granularity != "granular_char_gradient_str":
            granularity = "simple_char_gradient_str"
        self.granularity: str = granularity
        self.cache: Dict[CharData, CharData] = {}
        self.use_cache = use_cache

    def print_ascii_output(self):
        per_row = get_chars_per_row(self.image, self.reduce_ratio)
        processed_data: List[ProcessedImageChunkData] = self.convert_image_to_ascii()
        row_chars = ""
        for i in range(len(processed_data)):
            row_chars+=chr(processed_data[i]["character"])+" "
            if (i + 1) % per_row  == 0:
                print(row_chars)
                row_chars = ""
        

    def convert_image_to_ascii(self) -> List[ProcessedImageChunkData]:
        chunk_data: List[List[CharSubRegionData]] = image_chunk_meta_mapper(generate_character_sub_region_data, self.image, self.reduce_ratio)
        greyscaled_chunk_data = []
        for chunk in chunk_data:
            greyscaled_chunk_data.append(list(map(greyscale_subRegionData, chunk)))
        image_chunk_lexical_reps: List[CharData] = list(map(char_string_representation_reducer, greyscaled_chunk_data))
        lexical_reps = []
        cache_hits = 0
        for im_chunk_data in image_chunk_lexical_reps:
            lowest_dist = [(99, 0)] #dist: char
            if self.use_cache and im_chunk_data[self.granularity] in self.cache:
                lowest_dist = self.cache[im_chunk_data[self.granularity]]
                cache_hits+=1
            else:
                for char in self.char_map[self.granularity]:
                    dist = nltk.edit_distance(im_chunk_data[self.granularity], char)
                    if dist < lowest_dist[0][0]:
                        lowest_dist = [(dist,self.char_map[self.granularity][char] )]
                    elif dist == lowest_dist[0][0]:
                        lowest_dist.append((dist,self.char_map[self.granularity][char] ))
                self.cache[im_chunk_data[self.granularity]] = lowest_dist
            chosen = random.choice(lowest_dist)
            # lexical_reps.append({"character": chosen[1]})
            lexical_reps.append({"character": lowest_dist[0][1]})
        print("cache hits", cache_hits)
        return lexical_reps