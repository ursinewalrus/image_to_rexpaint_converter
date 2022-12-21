from typing import Dict
import PIL
import nltk
from lib.types import *
from lib.image_traversal_utils import *
import json


# https://stackoverflow.com/questions/55487618/looking-for-python-library-which-can-perform-levenshtein-other-edit-distance-at
class ImageToAscii:

    def __init__(self, image_path: str, char_map_filepath: str, reduce_ratio: int,
                 granularity: str = ImageGranularity.SIMPLE, black_and_white: bool = False):
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
        self.use_cache = True
        self.black_and_white = black_and_white
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
            if not self.black_and_white:
                row_chars += "\x1b[38;2;" + color_str + chr(processed_data[i].character_literal) + "\x1b[0m "
            else:
                row_chars +=chr(processed_data[i].character_literal)+" "
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

    # converted_row_len
    def post_processing_edge_adder(self,  ascii_image_data: List[ProcessedImageChunkData]) -> List[ProcessedImageChunkData]:
        """
        initial pass:
            var: region_averaging_size(yeech...): how for to look on each side of each chunk to determine "regions"
               average_distance_diff(edit_distance) between chunks within a region span: get average of each pair, then everage the averages?
               average_RGB_diff distance between chunks with a region span: get average of each pair, then everage the averages?

            all above - record, get the new, total image average

            distance_threshhold: fraction or % of <dist between 2 chunks>/average_distance_diff that determines when to call the diffeerence between two blocks an edge,
            RGB_threshold: fraction or % of <dist between 2 chunks>/average_RGB_diff that determines when to call the diffeerence between two blocks an edge,
        second pass:


            sub in new chars for edges where edges detected, going through and calulcating diffs between chunks in all dirs and determining if

            dist avg: 5, current 4, threshold .5 |   abs(5-4) / 5 = .2  < .5 - no edge
            dist ave: 5, current 8, thrshold .5  |   abs(5/8) / 5 = .6 > .5  - no edge

            Can only be an edge if it is exceded in 2 or less dirs, more than that and its more likely an island

            if we detect an edge to our current right, when we move over one we should expect to see an edge on the next one overs right.
            Unclear solution here as an edge should only be 1 char thick

        char substitution:
            placement - either all shifted one dir or random?
            char: for start perhaps just "." - also perhaps blank spaces, preset edge chars, derive new char from a combo of the edge zone


        NOTE: FOR THE CHAR MAPPING JSON MAYBE SUM UP THE BLACK SPACE ON EACH CHAR< DIVIDE It oR WHAtnot TO GET AN AVG DARKNESS AND SET
        # THAT AS THE LEXICAL STRING CHAR USED FOR ITS PATTERN, SO THAT CHARS WITH LESS IN THEM WILL BE SET AS FOR LIGHTER SECTIONS
        IN GENERAL, BASICALLY INCORPOARTING A BIT OF THE OLD TRICK FOR BASIC ASCII SGTUFF

        """

        region_detection_span = 2 # should be class var
        distance_threshold = .5 # should be a class var
        RGB_threshold = .5 # dunno what makes sense here either

        # for idx,chunk in enumerate(ascii_image_data):


        pass

    def get_adjacent_chunks(self, idx, span, ascii_image_data ) -> AdjacentChunks:
        pass