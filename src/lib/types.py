from typing import Tuple, TypedDict

class CharSubRegionData(TypedDict):
	pixel_sums: Tuple[int, int, int]
	cords: str # 'X:Y'

class CharData(TypedDict):
	simple_char_gradient_str: str
	granular_char_gradient_str: str
	summed_simple_gradient: int
	summed_granular_gradient: int

class ProcessedImageChunkData(TypedDict):
	character: str
	location: str
	foreground_color: Tuple[int, int, int]
	background_color: Tuple[int, int, int]