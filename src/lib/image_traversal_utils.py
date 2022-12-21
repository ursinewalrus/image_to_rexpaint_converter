import math

from PIL.Image import Image
from typing import Callable
from functools import reduce

from typing import List

from src.lib.types import CharSubRegionData, CharData


def char_string_representation_reducer(greyscaled_char_data: List[CharSubRegionData]) -> CharData:
    simple_char_gradient_str: str = "" #A-H
    granular_char_gradient_str: str = ""#A-Z

    gradient_squasher = lambda squash_factor: round((csrd["pixel_sums"][0] / 255) * (squash_factor - 1))

    # get avg greyscale val for whole subregion for scaling subsequent vals, 0.0 is pure black, 255 pure white
    avg_greyscale_val_of_char = reduce(lambda acc, char_chunk: acc+char_chunk["pixel_sums"][0], greyscaled_char_data, 0  ) / 9
    # print("AVG GRY IS", avg_greyscale_val_of_char)
    # should use the fraction of this to get another scale to apply to our chars maps
    # so if our num is 51 our ration is 4/5ths pure black, take our simple or complex val and do...something with it
    # AVG is 127, exact halfway beween all white and all black - keep our original result form teh gradient_squasher
    # AVG is 0, all black(AAAAAAAAA) - divide result out of that by 2, whole char is represented as a darker string(lower letters)
    # AGG is 255 all white (HHHHHHHHH or ZZZZZZZZZ) multiply result out by 2, whole char is represented as a lighter string(higher letters)
    # - MUST BE DONE OFF THE AVG OF THE ENTIRE SET OF CHARS MAYBE???? DO SOME FANCY MATH TO GET NEW BOUNDS??
    # likely too much squash
    brightness_scaler = 1
    if avg_greyscale_val_of_char > 128:
        brightness_scaler = avg_greyscale_val_of_char / 128
    elif avg_greyscale_val_of_char < 127:
        brightness_scaler = .5 + avg_greyscale_val_of_char / 256

    # print("***")
    # print(avg_greyscale_val_of_char)
    # print(brightness_scaler)
    for csrd in greyscaled_char_data:

        offset = 65 # A
        simple_val = gradient_squasher(8)
        if brightness_scaler > 1:
            simple_val = min(math.ceil(simple_val * brightness_scaler),7)
        else:
            simple_val = min(math.floor(simple_val * brightness_scaler),7)

        complex_val = gradient_squasher(26)
        simple_char_gradient_str += chr(offset + simple_val)
        granular_char_gradient_str += chr(offset + complex_val)
    summed_simple_gradient = reduce(lambda acc, char: acc+ord(char), list(simple_char_gradient_str), 0)
    summed_granular_gradient = reduce(lambda acc, char: acc+ord(char), list(granular_char_gradient_str), 0)
    return {"simple_char_gradient_str": simple_char_gradient_str, 
            "granular_char_gradient_str": granular_char_gradient_str,
            # summed ones not zipped into output
            "summed_simple_gradient": summed_simple_gradient,
            "summed_granular_gradient": summed_granular_gradient
            }


def image_chunk_meta_mapper(fn: Callable, image: Image, chunk_size: int):
    im_w, im_y = image.size[0], image.size[1]
    cropped_w = im_w - (im_w % chunk_size)
    cropped_y = im_y - (im_y % chunk_size)

    return_vals = []
    total_chars = 0
    for y in range(0,cropped_y, chunk_size):
        for x in range(0, cropped_w, chunk_size):
            region = image.crop((x, y, x + chunk_size, y + chunk_size))
            return_vals.append(fn(region))
            total_chars+=1
    return return_vals

def generate_character_sub_region_data(char_region : Image) -> List[CharSubRegionData]:
    """
    In a 20 pixel across image will make sections of size 8x8/8x8/8x8 with overlapping pixels
    1  2  3  4  5  6  7  8
    7  8  9  10 11 12 13 14
    13 14 15 16 17 18 19 20
    """
    char_sub_region_RGB_averages: List[CharSubRegionData] = []
    # divide it into 9 parts
    sub_region_size_w, sub_region_size_y  = char_region.size[0] // 3, char_region.size[1] // 3

    
    overlap_pixels_x = char_region.size[0] % sub_region_size_w

    overlap_pixels_y : int  = char_region.size[1] % sub_region_size_y

    x_pixels_to_go = 0
    y_pixels_to_go = 0

    grid_x = 0
    grid_y = 0

    while y_pixels_to_go < char_region.size[1] - overlap_pixels_y: 

        y_pixels : int = sub_region_size_y
        if overlap_pixels_y > 0:
            y_pixels += overlap_pixels_y

        while x_pixels_to_go < char_region.size[0] - overlap_pixels_x: 
            
            x_pixels = sub_region_size_w
            if overlap_pixels_x > 0:
                x_pixels += overlap_pixels_x


            sub_region : Image = char_region.crop((x_pixels_to_go, y_pixels_to_go, x_pixels_to_go + x_pixels, y_pixels_to_go + y_pixels)) 
            pixels = list(sub_region.getdata())  
            char_pixel_number = len(pixels)
            pixel_sums = reduce(lambda acc, pix: (pix[0] + acc[0], \
                                pix[1] + acc[1], \
                                pix[2] + acc[2] ), 
                                pixels)
            pixel_sums = (pixel_sums[0] // char_pixel_number,
                            pixel_sums[1] // char_pixel_number,
                            pixel_sums[2] // char_pixel_number )

            char_sub_region_RGB_averages.append({"pixel_sums": pixel_sums, "cords":f"{grid_x}:{grid_y}" })

            x_pixels_to_go += sub_region_size_w
            # print(f"CORDS: {grid_x}:{grid_y} | AVG: ({','.join(map(str, pixel_sums))})")
            grid_x += 1

        x_pixels_to_go = 0

        y_pixels_to_go += sub_region_size_y

        grid_x = 0
        grid_y += 1
    return char_sub_region_RGB_averages

def generate_character_sub_region_data_non_overlapping_ranges(self, char_region : Image) -> List[CharSubRegionData]:
    """
    In a 20 pixel across image will make sections of size 7x7/7x7/6x6
    """
    char_sub_region_RGB_averages: List[CharSubRegionData] = []
    # divide it into 9 parts
    sub_region_size_w, sub_region_size_y  = char_region.size[0] // 3, char_region.size[1] // 3

    
    extra_pixels_w = char_region.size[0] % sub_region_size_w
    extra_pixels_w_reset_value = extra_pixels_w

    extra_pixels_y : int  = char_region.size[1] % sub_region_size_y

    x_pixels_parsed = 0
    y_pixels_parsed = 0

    grid_x = 0
    grid_y = 0

    while y_pixels_parsed < char_region.size[1]:

        y_pixels : int = sub_region_size_y
        if extra_pixels_y > 0:
            y_pixels += 1
            extra_pixels_y -= 1

        while x_pixels_parsed < char_region.size[0]:
            
            x_pixels = sub_region_size_w
            if extra_pixels_w > 0:
                x_pixels += 1
                extra_pixels_w -= 1


            sub_region : Image = char_region.crop((x_pixels_parsed, y_pixels_parsed, x_pixels_parsed + x_pixels, y_pixels_parsed + y_pixels)) 
            # sub_region.show() #type: ignore
            pixels = list(sub_region.getdata()) 
            char_pixel_number = len(pixels)
            pixel_sums = reduce(lambda acc, pix: (pix[0] + acc[0], \
                                pix[1] + acc[1], \
                                pix[2] + acc[2] ), 
                                pixels)
            pixel_sums = (pixel_sums[0] // char_pixel_number,
                            pixel_sums[1] // char_pixel_number,
                            pixel_sums[2] // char_pixel_number )

            char_sub_region_RGB_averages.append({"pixel_sums": pixel_sums, "cords":f"{grid_x}:{grid_y}" })

            x_pixels_parsed += x_pixels
            # print(f"CORDS: {grid_x}:{grid_y} | AVG: ({','.join(map(str, pixel_sums))})")
            grid_x += 1

        x_pixels_parsed = 0
        extra_pixels_w = extra_pixels_w_reset_value

        y_pixels_parsed += y_pixels

        grid_x = 0
        grid_y += 1
        # need to reset extra_pixels_w as well ...
    return char_sub_region_RGB_averages

def greyscale_subRegionData(subRegionData: CharSubRegionData) -> CharSubRegionData:
    greyscale_val = (subRegionData["pixel_sums"][0] + subRegionData["pixel_sums"][1] + subRegionData["pixel_sums"][2]) // 3
    return {"pixel_sums":(greyscale_val,greyscale_val,greyscale_val), "cords":subRegionData["cords"] }

def get_avg_subRegionColor(subRegionData: List[CharSubRegionData]) -> tuple[int, int, int]:
    r_avg = reduce(lambda acc, c: c["pixel_sums"][0] + acc, subRegionData, 0) // 9
    g_avg = reduce(lambda acc, c: c["pixel_sums"][1] + acc, subRegionData, 0) // 9
    b_avg = reduce(lambda acc, c: c["pixel_sums"][2] + acc, subRegionData, 0) // 9
    return (r_avg,g_avg,b_avg)

