from typing import Dict
import PIL
import nltk
from lib.types import *
from lib.image_traversal_utils import *
import json


# https://stackoverflow.com/questions/55487618/looking-for-python-library-which-can-perform-levenshtein-other-edit-distance-at
class ImageToAscii:

    def __init__(self, image_path: str, char_map_filepath: str, reduce_ratio: int,
                 granularity: str = ImageGranularity.SIMPLE, use_cache: bool = True):
        self.image: Image = PIL.Image.open(image_path)
        # with open(char_map_filepath) as map_data:
        #     self.map_data = json.load(map_data)
        with open(char_map_filepath) as f:
            self.char_map = json.load(f)
        # must be at least 3
        if reduce_ratio < 3:
            reduce_ratio = 3
        self.reduce_ratio: int = reduce_ratio

        if granularity != ImageGranularity.GRANULAR:
            granularity = ImageGranularity.SIMPLE
        self.granularity: ImageGranularity = granularity.value
        self.cache: Dict[CharData, CharData] = {}
        self.use_cache = use_cache
        self.converted_row_len = self.get_chars_per_row(self.image, self.reduce_ratio)

    def get_chars_per_row(self, image, chunk_size):
        im_w = image.size[0]
        cropped_w = im_w - (im_w % chunk_size)
        return cropped_w // chunk_size

    def convert_and_package_for_export(self) -> ConvertedPackagedImageData:
        converted_image: List[ProcessedImageChunkData] = self.convert_image_to_ascii()
        # more meta here later surely...
        return ConvertedPackagedImageData(converted_image, self.converted_row_len)

    def print_ascii_output(self):
        processed_data: List[ProcessedImageChunkData] = self.convert_image_to_ascii()
        row_chars = ""
        for i in range(len(processed_data)):
            color_str = ";".join(map(str, list(processed_data[i].foreground_color))) + "m"
            row_chars += "\x1b[38;2;" + color_str + chr(processed_data[i].character_literal) + "\x1b[0m "
            # row_chars+=chr(processed_data[i]["character"])+" "
            if (i + 1) % self.converted_row_len == 0:
                print(row_chars)
                row_chars = ""

    def convert_image_to_ascii(self) -> List[ProcessedImageChunkData]:
        # make this 2d, rotate it should alter output orientation
        chunk_data: List[List[CharSubRegionData]] = image_chunk_meta_mapper(generate_character_sub_region_data,
                                                                            self.image, self.reduce_ratio)
        greyscaled_chunk_data = []
        for chunk in chunk_data:
            greyscaled_chunk_data.append(list(map(greyscale_subRegionData, chunk)))
        image_chunk_lexical_reps: List[CharData] = list(map(char_string_representation_reducer, greyscaled_chunk_data))
        lexical_reps: List[ProcessedImageChunkData] = []
        cache_hits = 0
        for idx, im_chunk_data in enumerate(image_chunk_lexical_reps):
            lowest_dist = [(99, 0)]  # dist: char
            if self.use_cache and im_chunk_data[self.granularity] in self.cache:
                lowest_dist = self.cache[im_chunk_data[self.granularity]]
                cache_hits += 1
            else:
                for lexical_char_rep in self.char_map[self.granularity]:
                    dist = nltk.edit_distance(im_chunk_data[self.granularity], lexical_char_rep)
                    if dist < lowest_dist[0][0]:
                        lowest_dist = [(dist, self.char_map[self.granularity][lexical_char_rep])]
                    elif dist == lowest_dist[0][0]:
                        lowest_dist.append((dist, self.char_map[self.granularity][lexical_char_rep]))
                self.cache[im_chunk_data[self.granularity]] = lowest_dist
            # chosen = random.choice(lowest_dist)
            # lexical_rep = {"character": chosen[1]}
            lexical_rep = ProcessedImageChunkData( lowest_dist[0][1][0],
                                                   lowest_dist[0][1][1],
                                                  0,
                                                  get_avg_subRegionColor(chunk_data[idx]),
                                                  (0,0,0))
            # lexical_rep = {"character": lowest_dist[0][1]}

            # mix in color
            # lexical_rep["foreground_color"] = get_avg_subRegionColor(chunk_data[idx])
            # 

            lexical_reps.append(lexical_rep)

            # lexical_reps.append({"character": lowest_dist[0][1]})
        print("cache hits", cache_hits)
        return lexical_reps
