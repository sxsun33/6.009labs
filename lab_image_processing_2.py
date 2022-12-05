#!/usr/bin/env python3

# NO ADDITIONAL IMPORTS!
# (except in the last part of the lab; see the lab writeup for details)
import math
from PIL import Image


# VARIOUS FILTERS

def get_pixel(image, x, y, boundary_behavior):
    '''
    Access the values of the pixels that are both in and out of range of the image depending on the boundary behavior
    For pixels that are out of range, the function goes through 8 possible cases (a combination of x/y having negative indices,
    indices greater than the width/height, and indices within range of the image) for each boundary behavior.
    For pixels within range, With x as the position of the pixel along the height and y as the position of the pixel along the width, 
    the pixel's corresponding index is width*x + y. 

    '''

    if x < 0 or y < 0 or x >= image['height'] or y >= image['width']:
        if boundary_behavior == 'zero':
            return 0
        
        if boundary_behavior == 'extend':
            if x < 0 and y < 0:
                return image['pixels'][0]
            elif x < 0 and y >= 0 and y < image['width']:
                return image['pixels'][y]
            elif x < 0 and y >= image['width']:
                return image['pixels'][image['width'] - 1]
            elif x >= 0 and x < image['height'] and y < 0:
                return image['pixels'][image['width']*x]
            elif x >= 0 and x < image['height'] and y >= image['width']:
                return image['pixels'][image['width']*(x + 1) - 1]
            elif x >= image['height'] and y < 0:
                return image['pixels'][len(image['pixels']) - image['width']]
            elif x >= image['height'] and y >= 0 and y < image['width']:
                return image['pixels'][len(image['pixels']) - image['width'] + y]
            elif x >= image['height'] and y >= image['width']:
                return image['pixels'][len(image['pixels']) - 1]
                    
        if boundary_behavior == 'wrap':
            if x < 0 and y < 0:
                x = image['height'] - (-x)%image['height']
                y = image['width'] - (-y)%image['width']
                get_pixel(image, x, y, None)
            elif x < 0 and y >= 0 and y < image['width']:
                x = image['height'] - (-x)%image['height']
                get_pixel(image, x, y, None)
            elif x < 0 and y >= image['width']:
                x = image['height'] - (-x)%image['height']
                y = y%image['width']
                get_pixel(image, x, y, None)
            elif x >= 0 and x < image['height'] and y < 0:
                y = image['width'] - (-y)%image['width']
                get_pixel(image, x, y, None)
            elif x >= 0 and x < image['height'] and y >= image['width']:
                y = y%image['width']
                get_pixel(image, x, y, None)
            elif x >= image['height'] and y < 0:
                x = x%image['height']
                y = image['width'] - (-y)%image['width']
                get_pixel(image, x, y, None)
            elif x >= image['height'] and y >= 0 and y < image['width']:
                x = x%image['height']
                get_pixel(image, x, y, None)
            elif x >= image['height'] and y >= image['width']:
                x = x%image['height']
                y = y%image['width']
                get_pixel(image, x, y, None)

    return image['pixels'][image['width']*x + y]

def set_pixel(image, x, y, c):
    image['pixels'][image['width']*x + y] = c

def apply_per_pixel(image, func, boundary_behavior):
    result = {
        'height': image['height'],
        'width': image['width'],
        'pixels': [],
    }
    for x in range(image['height']):
        for y in range(image['width']):
            color = get_pixel(image, x, y, boundary_behavior)
            newcolor = func(color)
            result['pixels'].append(newcolor)
    return result

def inverted(image):
    return apply_per_pixel(image, lambda c: 255-c, None)

def correlate(image, kernel, boundary_behavior):
    """
    Compute the result of correlating the given image with the given kernel.
    `boundary_behavior` will one of the strings 'zero', 'extend', or 'wrap',
    and this function will treat out-of-bounds pixels as having the value zero,
    the value of the nearest edge, or the value wrapped around the other edge
    of the image, respectively.

    if boundary_behavior is not one of 'zero', 'extend', or 'wrap', return
    None.

    Otherwise, the output of this function should have the same form as a 6.101
    image (a dictionary with 'height', 'width', and 'pixels' keys), but its
    pixel values do not necessarily need to be in the range [0,255], nor do
    they need to be integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    Kernel is represented as a list similar to that of pixels, and the length 
    of the sides of the kernel can be calculated by taking the square root of the 
    length of the kernel list.
    """
    if boundary_behavior != 'zero' and boundary_behavior != 'extend' and boundary_behavior != 'wrap':
        return None
    
    side_length = int(math.sqrt(len(kernel)))
    mid_length = side_length//2

    pixels_applied_kernel = []

    #iterate through each pixel and apply the kernel to it
    for i in range(len(image['pixels'])):
        #calculating x and y using the index relation found in get_pixel (i = image['width']*x + y)
        x = i // image['width']
        y = i % image['width']

        pixel_applied = 0
        
        #start from the first element of the kernel and append values to the total kernel value associated with a particular index
        for j in range(side_length):
            for k in range(side_length): 
                x_index = x - mid_length + j
                y_index = y - mid_length + k
                pixel_applied += get_pixel(image, x_index, y_index, boundary_behavior) * kernel[side_length*j + k]
        
        pixels_applied_kernel.append(pixel_applied)

    return {'height': image['height'], 'width': image['width'], 'pixels': pixels_applied_kernel}
    

def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the 'pixels' list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """
    rounded_pixels = []

    for pixel in image['pixels']:
        #set negative pixel values to zero; set pixel values above 255 to 255
        if pixel < 0:
            pixel = 0
        elif pixel > 255:
            pixel = 255
        else:
            pixel = round(pixel)
        rounded_pixels.append(pixel)
    return {'height': image['height'], 'width': image['width'], 'pixels': rounded_pixels}

def split_image(image):
    '''
    Splits a colored image into its three components
    '''
    red_pixels = []
    green_pixels = []
    blue_pixels = []

    for pixel in image['pixels']:
        red_pixels.append(pixel[0])
        green_pixels.append(pixel[1])
        blue_pixels.append(pixel[2])
    
    red_image = {'height': image['height'], 'width': image['width'], 'pixels': red_pixels}
    green_image = {'height': image['height'], 'width': image['width'], 'pixels': green_pixels}
    blue_image = {'height': image['height'], 'width': image['width'], 'pixels': blue_pixels}

    return red_image, green_image, blue_image

def color_filter_from_greyscale_filter(filt):
    """
    Given a filter that takes a greyscale image as input and produces a
    greyscale image as output, returns a function that takes a color image as
    input and produces the filtered color image.
    """
    def split_colors_then_recombine_filtered(image):

        colored_pixels_filtered = []

        red_image, green_image, blue_image = split_image(image)

        red_image_filtered = filt(red_image)
        green_image_filtered = filt(green_image)
        blue_image_filtered = filt(blue_image)

        for i in range(len(image['pixels'])):
            colored_pixels_filtered.append((red_image_filtered['pixels'][i], green_image_filtered['pixels'][i], blue_image_filtered['pixels'][i]))
        
        return {'height': image['height'], 'width': image['width'], 'pixels': colored_pixels_filtered}
    
    return split_colors_then_recombine_filtered

filter = color_filter_from_greyscale_filter(inverted)


def make_blur_filter(n):
    
    def blurred_filtered(image):

        return round_and_clip_image(correlate(image, [(1/n**2)] * n**2, 'extend'))

    return blurred_filtered


def make_sharpen_filter(n):
    
    def sharpened_filtered(image):

        kernel = [- (1/n**2)] * n**2
        kernel[(n**2)//2] = 2 - (1/n**2)

        return round_and_clip_image(correlate(image, kernel, 'extend'))

    return sharpened_filtered

def edges(image):
    """
    Return a new image representing the result of applying a sharpen filter (with
    kernel size n) to the given input image.
    """
    K_x = [-1, 0, 1, -2, 0, 2, -1, 0, 1]
    K_y = [-1, -2, -1, 0, 0, 0, 1, 2, 1]
    ox = correlate(image, K_x, 'extend')['pixels']    
    oy = correlate(image, K_y, 'extend')['pixels']
    image_edge_detection = []

    for i in range(len(image['pixels'])):
        image_edge_detection.append(round((ox[i]**2 + oy[i]**2)**(1/2)))
    
    new_image = {'height': image['height'], 'width': image['width'], 'pixels': image_edge_detection}
    return round_and_clip_image(new_image)


def filter_cascade(filters_list):
    """
    Given a list of filters (implemented as functions on images), returns a new
    single filter such that applying that filter to an image produces the same
    output as applying each of the individual ones in turn.
    """
    def cascade_image(image):

        for filter in filters_list:
             image = filter(image)
        
        return image
    
    return cascade_image


# SEAM CARVING

# Main Seam Carving Implementation


def seam_carving(image, ncols):
    """
    Starting from the given image, use the seam carving technique to remove
    ncols (an integer) columns from the image. Returns a new image.
    """
    new_image = {'height': image['height'], 'width': image['width'], 'pixels': image['pixels'][:]}

    for i in range(ncols):
        greyscale_image = greyscale_image_from_color_image(new_image)
        energy_image = compute_energy(greyscale_image)
        c_energy_map = cumulative_energy_map(energy_image)
        seam = minimum_energy_seam(c_energy_map)
        new_image = image_without_seam(new_image, seam)
    
    return new_image

# Optional Helper Functions for Seam Carving


def greyscale_image_from_color_image(image):
    """
    Given a color image, computes and returns a corresponding greyscale image.

    Returns a greyscale image (represented as a dictionary).
    """
    greyscale_pixels = []

    for pixel in image['pixels']:
        v = round(0.299 * pixel[0] + 0.587 * pixel[1] + 0.114 * pixel[2])
        greyscale_pixels.append(v)
    
    return {'height': image['height'], 'width': image['width'], 'pixels': greyscale_pixels}


def compute_energy(grey):
    """
    Given a greyscale image, computes a measure of "energy", in our case using
    the edges function from last week.

    Returns a greyscale image (represented as a dictionary).
    """
    return edges(grey)


def cumulative_energy_map(energy):
    """
    Given a measure of energy (e.g., the output of the compute_energy
    function), computes a "cumulative energy map" as described in the lab 2
    writeup.

    Returns a dictionary with 'height', 'width', and 'pixels' keys (but where
    the values in the 'pixels' array may not necessarily be in the range [0,
    255].

    For each row of the "cumulative energy map":
     For each pixel in the row:
         Set this value in the "cumulative energy map" to be:
           the value of that location in the energy map, added to the
           minimum of the cumulative energies from the "adjacent" pixels in the row
           above
    """
    c_e_m = {'height': energy['height'], 'width': energy['width'], 'pixels': energy['pixels']}

    for x in range(c_e_m['height']):
        for y in range(c_e_m['width']):
            index = c_e_m['width']*x + y
            index_row_above = c_e_m['width']*(x - 1) + y
            if x != 0:
                #consider pixels at the edges to make sure the pixel extracted is not out of range; compute the minimum of the adjacent pixels of the row above and set the cumulative energy as the minimum + pixel at the current location
                if y == 0:
                    c_e_m['pixels'][index] = c_e_m['pixels'][index] + min(c_e_m['pixels'][index_row_above], c_e_m['pixels'][index_row_above + 1])

                elif y == c_e_m['width'] - 1:
                    c_e_m['pixels'][index] = c_e_m['pixels'][index] + min(c_e_m['pixels'][index_row_above], c_e_m['pixels'][index_row_above - 1])

                else: 
                    c_e_m['pixels'][index] = c_e_m['pixels'][index] + min(c_e_m['pixels'][index_row_above], c_e_m['pixels'][index_row_above - 1], c_e_m['pixels'][index_row_above + 1])

    return c_e_m
    

def minimum_energy_seam(cem):
    """
    Given a cumulative energy map, returns a list of the indices into the
    'pixels' list that correspond to pixels contained in the minimum-energy
    seam (computed as described in the lab 2 writeup).
    """

    indices_to_be_seamed = []

    for x in range(cem['height']):

        #find the minimum of the last row and append the index onto indices_to_be_seamed
        if x == 0:
            first_index = (cem['height']- 1) * cem['width']
            last_index = (cem['height']) * cem['width']
            row_list = cem['pixels'][first_index : last_index]

            min_energy = min(row_list)

            indices_with_minimum_value = []
        
            for idx, value in enumerate(row_list):
                if value == min_energy:
                    indices_with_minimum_value.append(idx + (cem['height']- 1) * cem['width'])
        
            indices_to_be_seamed.append(min(indices_with_minimum_value))
        
        else:
            #find the last index appended to indices_to_be_seamed to determine the adjacent pixels of the row above
            latest_index = indices_to_be_seamed[len(indices_to_be_seamed) - 1]
            
            #consider if the last index appended to indices_to_be_seamed is on the edge of the image
            if latest_index % cem['width'] == 0:

                first_index = latest_index - cem['width']

                #in the case in which both adjacent pixel return the minimum value, return the indices of the left pixel
                if cem['pixels'][first_index] == cem['pixels'][first_index + 1]: indices_to_be_seamed.append(first_index)

                else:
                    
                    if cem['pixels'][first_index] < cem['pixels'][first_index + 1]: indices_to_be_seamed.append(first_index)

                    else: indices_to_be_seamed.append(first_index + 1)
            
            elif (latest_index % cem['width']) == (cem['width'] - 1):

                first_index = latest_index - cem['width'] - 1

                if cem['pixels'][first_index] == cem['pixels'][first_index + 1]: indices_to_be_seamed.append(first_index)

                else:

                    if cem['pixels'][first_index] < cem['pixels'][first_index + 1]: indices_to_be_seamed.append(first_index)

                    else: indices_to_be_seamed.append(first_index + 1)                    
                
            else:
                first_index = latest_index - cem['width'] - 1
                min_energy_list = cem['pixels'][first_index : first_index + 3]
                min_energy = min(min_energy_list)

                indices_with_minimum_value = []
        
                for idx, value in enumerate(min_energy_list):
                    if value == min_energy:
                        indices_with_minimum_value.append(idx + latest_index - cem['width'] - 1)
                
                indices_to_be_seamed.append(min(indices_with_minimum_value))

    return indices_to_be_seamed

def image_without_seam(image, seam):
    """
    Given a (color) image and a list of indices to be removed from the image,
    return a new image (without modifying the original) that contains all the
    pixels from the original image except those corresponding to the locations
    in the given list.
    """
    #remove pixels from the back so the previous indices wouldn't be affected
    pixels_removed = image['pixels']
    index_removed = list(sorted(seam))
    index_removed = index_removed[::-1]

    for index in index_removed:
        pixels_removed.pop(index)

    return {'height': image['height'], 'width': image['width'] - 1, 'pixels': pixels_removed}

def custom_feature(image):
    '''
    Given a (color) image return a new image that contains pixels with r = (r + g)/2, g = (g + b)/2, b = (b + r)/2; creating an image that bases its pixels on secondary colors
    '''
    new_pixels = []

    for pixel in image['pixels']:

        average_tuple = (pixel[0] + pixel[1])//2, (pixel[1] + pixel[2])//2, (pixel[2] + pixel[0])//2
        new_pixels.append(tuple(average_tuple))
    
    return {'height': image['height'], 'width': image['width'], 'pixels': new_pixels}
        

# HELPER FUNCTIONS FOR LOADING AND SAVING COLOR IMAGES


def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

    Invoked as, for example:
       i = load_color_image('test_images/cat.png')
    """
    with open(filename, "rb") as img_handle:
        img = Image.open(img_handle)
        img = img.convert("RGB")  # in case we were given a greyscale image
        img_data = img.getdata()
        pixels = list(img_data)
        w, h = img.size
        return {"height": h, "width": w, "pixels": pixels}


def save_color_image(image, filename, mode="PNG"):
    """
    Saves the given color image to disk or to a file-like object.  If filename
    is given as a string, the file type will be inferred from the given name.
    If filename is given as a file-like object, the file type will be
    determined by the 'mode' parameter.
    """
    out = Image.new(mode="RGB", size=(image["width"], image["height"]))
    out.putdata(image["pixels"])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns an instance of this class
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image('test_images/cat.png')
    """
    with open(filename, "rb") as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith("RGB"):
            pixels = [
                round(0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]) for p in img_data
            ]
        elif img.mode == "LA":
            pixels = [p[0] for p in img_data]
        elif img.mode == "L":
            pixels = list(img_data)
        else:
            raise ValueError("Unsupported image mode: %r" % img.mode)
        w, h = img.size
        return {"height": h, "width": w, "pixels": pixels}


def save_greyscale_image(image, filename, mode="PNG"):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the 'mode' parameter.
    """
    out = Image.new(mode="L", size=(image["width"], image["height"]))
    out.putdata(image["pixels"])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


if __name__ == "__main__":
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.
    
    # if we have a greyscale filter called inverted that inverts a greyscale
    # image...
    #inverted_grey_cat = inverted(load_greyscale_image('grey_frog.png'))
    #inverted_grey_frog = inverted(load_greyscale_image('cat.png'))

    # then the following will create a color version of that filter
    #filter1 = color_filter_from_greyscale_filter(edges)
    #filter2 = color_filter_from_greyscale_filter(make_blur_filter(5))
    #filt = filter_cascade(list([filter1, filter1, filter2, filter1]))

    #color_cascade = color_filter_from_greyscale_filter(filt)

    # that can then be applied to color images to invert them (note that this
    # should make a new color image, rather than mutating its input)
    flood_input = custom_feature(load_color_image('flood_input.png'))
    print(flood_input['height'])
    print(flood_input['width'])