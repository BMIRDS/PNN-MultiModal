from openslide import OpenSlide
from pathlib import Path
from PIL import Image, ImageEnhance, ImageDraw, ImageOps, ImageCms
from io import BytesIO
import argparse
import csv
import math
import os
import re


ROI_ROW_OFFSET = 15
TARGET_SLIDES={
    1: "TMA1054_HuWTA",
    2: "TMA1054_HuWTA_2"
}
CHANNEL_MULTIPLIER = 10
def parse_arguments():
    parser = argparse.ArgumentParser(description='Process images and save output in specified directory.')
    parser.add_argument('-i', '--inputcsv', default='/datasets/PNN_study/TMA1054/TMA1054 hWTA_20230817T1508_LabWorksheet.csv', help='Path to CSV file with ROI information')
    parser.add_argument('-o', '--outputpath', default='test_images', help='Output directory path')
    parser.add_argument('-d', '--datadir', default='/datasets/PNN_study/TMA1054/', help='Data root dir')

    parser.add_argument('--tiff', type=int, default=2, help='TIFF number')
    parser.add_argument('--roi', type=int, default=50, help='ROI number')
    parser.add_argument('--test-case', action="store_true", default=False, 
                        help='Run a small test case for algorithm inspection.')
    return parser.parse_args()
    

def get_roi_info(csv_path):
    roi_infos = {}
    try:
        with open(csv_path, 'r', newline='') as csvfile:
            csv_reader = csv.reader(csvfile)
            for _ in range(ROI_ROW_OFFSET): # Skip rows until column labels
                next(csv_reader)
            column_labels = next(csv_reader) # Read column labels
            for row in csv_reader: # Process each row according to column labels
                if not row:  # Skip empty rows
                    continue
                row_info = {label: value for label, value in zip(column_labels, row)} # Create a dictionary for the row, mapping column label to value
                # Check if it contains valid information
                pattern = r'^\d{3}$'
                roi_value = row_info["Roi"]
                if not roi_value or (roi_value and not re.match(pattern, roi_value)):
                    continue
                roi_num = row_info["Roi"]
                slide_name = row_info["Slide Name"]
                slide_key = f"{slide_name}_{roi_num}"
                roi_infos[slide_key] = row_info
        return roi_infos
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None


def extract_roi(slide_path, roi_coord_x, roi_coord_y, area):
    estimated_radius = math.sqrt(area / math.pi) * 2.48
    size = (int(estimated_radius * 2), int(estimated_radius * 2))
    top_left_corner = (int(round(roi_coord_x - estimated_radius)), int(round(roi_coord_y - estimated_radius)))
    slide = OpenSlide(slide_path)
    #debug
    read_region_first = slide.read_region(location=top_left_corner, level=0, size=size)
    read_region_first.save("read_region_first.png")
    #

    # in case coords are out of bounds
    #slide_width = int(slide.properties['openslide.level[0].width'])
    #slide_height = int(slide.properties['openslide.level[0].height'])
    #if not (0 <= roi_coord_x < slide_width):
    #    raise ValueError("ROI X coordinate is out of slide bounds.")
    #if not (0 <= roi_coord_y < slide_height):
    #    raise ValueError("ROI Y coordinate is out of slide bounds.")
    
    # extract the image and make it circular
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0,0)+size, fill = 255) # 255 is "on" and 0 is "off". everything that's 0 is removed from the image when we apply the mask
    roi_image = slide.read_region(location=top_left_corner, level=0, size=size)
    # debug
    roi_image.save("COLORTEST.png", icc_profile=roi_image.info.get('icc_profile'))
    pixel = roi_image.getpixel((100,100))
    print(pixel)
    print("ICC_PROFILE:", roi_image.info.get('icc_profile'))
    #
    circle_roi_image = ImageOps.fit(roi_image, mask.size, centering =(0.5,0.5)) # make sure mask is positioned correctly
    circle_roi_image.putalpha(mask)
    print("ICC_PROFILE:", circle_roi_image.info.get('icc_profile'))
    circle_roi_image.convert("RGB")
    roi_image.save("RGB.png", icc_profile=roi_image.info.get('icc_profile'))

    thumbnailimage = slide.get_thumbnail(size=size)
    thumbnailimage.save("THUMBNAIL.png")

    print("READ REGION FOR JUST A PIXEL")
    rgb_values = slide.read_region(location = top_left_corner, level= 0, size=size).convert('RGB').getpixel((0, 0))
    print(rgb_values)
    slide.close()

    region_srgb = roi_image.convert("RGB")
    region_srgb.save("COLORING.png")

    ##### check color after extraction
    print("after extraction pixel rgb information for every pixel:")
    for x in range(620):
        for y in range(620):
            r, g, b, a = circle_roi_image.getpixel((x,y))
            #print(r, g, b, a)
    rgba_values = list(circle_roi_image.getdata())
    sum_r, sum_g, sum_b, sum_a = 0, 0, 0, 0
    for pixel in rgba_values:
        sum_r += pixel[0]
        sum_g += pixel[1]
        sum_b += pixel[2]
        sum_a += pixel[3]
    print("Sum of R channel:", sum_r)
    print("Sum of G channel:", sum_g)
    print("Sum of B channel:", sum_b)
    print("Sum of A channel:", sum_a)
    #####
    return circle_roi_image


def combine_images(img1, img2, vertically=True):
    try:
        # Resize images to match width or height for stacking
        if vertically:
            new_width = min(img1.width, img2.width)
            img1 = img1.resize((new_width, round(img1.height * (new_width / img1.width))))
            img2 = img2.resize((new_width, round(img2.height * (new_width / img2.width))))
            combined_size = (new_width, img1.height + img2.height)
            paste_positions = [(0, 0), (0, img1.height)]
        else:
            new_height = min(img1.height, img2.height)
            img1 = img1.resize((round(img1.width * (new_height / img1.height)), new_height))
            img2 = img2.resize((round(img2.width * (new_height / img2.height)), new_height))
            combined_size = (img1.width + img2.width, new_height)
            paste_positions = [(0, 0), (img1.width, 0)]

        # Create a new image with the size of the combined images
        combined_img = Image.new('RGBA' if img1.mode == 'RGBA' or img2.mode == 'RGBA' else 'RGB', combined_size)

        # Paste images onto the combined image
        for img, position in zip([img1, img2], paste_positions):
            combined_img.paste(img, position, mask=img.split()[3] if img.mode == 'RGBA' else None)
        return combined_img
    except Exception as e:
        print(f"Error combining images: {e}")
        return None


def adjust_brightness(circle_roi_image, brightness_factor):
    """
    Adjust extracted roi image brightness

    Input:
        circle_roi_image: PIL Image object
        brightness_factor: number of brightness (ie. 1.2 brighter, 0.8 darker)

    Output:
        Brightened PIL Image object
    """
    try:
        enhancer = ImageEnhance.Brightness(circle_roi_image)
        brightened_image = enhancer.enhance(brightness_factor)
        return brightened_image
    except Exception as e:
        return f"Error: {str(e)}"


def main():
    # args
    args = parse_arguments()
    csv_path = args.inputcsv
    outputpath = args.outputpath
    datadir = args.datadir
    Path(outputpath).mkdir(parents=True, exist_ok=True)

    # get roi info from corresponding slide
    roi_infos = get_roi_info(csv_path)
    roi_key = f"{TARGET_SLIDES[args.tiff]}_{args.roi:03}"
    roi_info = roi_infos[roi_key]

    # get the slide
    slide_path = f"{datadir}{roi_info['Scan Name']}.ome.tiff" # same as [SCAN NAME]
    slide = OpenSlide(slide_path)
    excludes = ["openslide.comment", "tiff.ImageDescription"]
    for k in slide.properties.keys():
        if len(k) > 100 or k in excludes:
            continue
        if len(slide.properties[k]) > 1000:
            print("Skip: ", k)
            continue
        print("PROPERTY", k, slide.properties[k])

    # extract image from slide
    circle_roi_image = extract_roi(
        slide_path=slide_path,
        roi_coord_x=float(roi_info['ROI Coordinate Y']),  # x and y are switched
        roi_coord_y=float(roi_info['ROI Coordinate X']),   # x and y are switched
        area=float(roi_info['Area']))
    bright_roi_image = adjust_brightness(circle_roi_image, 5.0)
    #bright_roi_image.save(Path(outputpath) / f"{roi_info['Scan Name']} - {args.roi:03}_bright.png")

    # compare result to reference
    ref_path = Path(args.datadir) / f"{roi_info['Scan Name']} ROIs" / f"{roi_info['Scan Name']} - {args.roi:03}.png"
    ref_image = Image.open(ref_path)
    combined_image = combine_images(bright_roi_image, ref_image, False)
    print("output image path", Path(outputpath) / f"{roi_info['Scan Name']} - {args.roi:03}-eval.png")
    combined_image.save(Path(outputpath) / f"{roi_info['Scan Name']} - {args.roi:03}-eval.png", icc_profile=combined_image.info.get('icc_profile'))

    profile = ImageCms.createProfile("sRGB")
    profile2 = ImageCms.ImageCmsProfile(profile)

    # Save image with profile
    combined_image.save(Path(outputpath) / f"NEWINFO.png", icc_profile=profile2.tobytes())


if __name__ == "__main__":
    main()
