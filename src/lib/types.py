from typing import Tuple, TypedDict, List

from enum import Enum


class CharSubRegionData(TypedDict):
    pixel_sums: Tuple[int, int, int]
    cords: str  # 'X:Y'


class CharData(TypedDict):
    simple_char_gradient_str: str
    granular_char_gradient_str: str
    summed_simple_gradient: int
    summed_granular_gradient: int


class ProcessedImageChunkData():
    def __init__(self, character_literal, character_rexpaint, location, foreground_color, background_color):
        self.character_literal: int = character_literal
        self.character_rexpaint: int = character_rexpaint
        self.location: str = location
        self.foreground_color: Tuple[int, int, int] = foreground_color
        self.background_color: Tuple[int, int, int] = background_color


class ConvertedPackagedImageData:
    def __init__(self, converted_image: List[ProcessedImageChunkData], row_len: int):
        self.converted_image: List[ProcessedImageChunkData] = converted_image
        self.row_len = row_len


class ImageGranularity(Enum):
    GRANULAR = "granular_char_gradient_str"
    SIMPLE = "simple_char_gradient_str"
