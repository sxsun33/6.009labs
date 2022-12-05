#!/usr/bin/env python3

import math

from PIL import Image as Image

# NO ADDITIONAL IMPORTS ALLOWED!

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

# HELPER FUNCTIONS

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


# FILTERS
def blurring_kernel(n):
    '''
    Takes in a single argument n and returns a box blur kernel with size n
    '''
    return [(1/n**2)] * n**2

def blurred(image, n):
    """
    Return a new image representing the result of applying a box blur (with
    kernel size n) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    kernel = blurring_kernel(n)
    return round_and_clip_image(correlate(image, kernel, 'extend'))

def sharpening_kernel(n):
    '''
    Takes in a single argument n and returns a box blur kernel with size n
    '''
    kernel = [- (1/n**2)] * n**2
    kernel[(n**2)//2] = 2 - (1/n**2)
    return kernel

def sharpened(image, n):
    """
    Return a new image representing the result of applying a sharpen filter (with
    kernel size n) to the given input image.
    """
    kernel = sharpening_kernel(n)
    return round_and_clip_image(correlate(image, kernel, 'extend'))

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

# HELPER FUNCTIONS FOR LOADING AND SAVING IMAGES

def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns a dictionary
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith('RGB'):
            pixels = [round(.299 * p[0] + .587 * p[1] + .114 * p[2])
                      for p in img_data]
        elif img.mode == 'LA':
            pixels = [p[0] for p in img_data]
        elif img.mode == 'L':
            pixels = list(img_data)
        else:
            raise ValueError('Unsupported image mode: %r' % img.mode)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_greyscale_image(image, filename, mode='PNG'):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the 'mode' parameter.
    """
    out = Image.new(mode='L', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.

    flood_input = load_greyscale_image("flood_input.png")
    print(flood_input['height'])
    



'''

        im_1 = {
        'height': 11,
        'width': 11,
        'pixels': [1, 2, 5, 25, 24, 50, 13, 255, 255, 7, 255,
                   255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 95,
                   255, 255, 255, 255, 255, 255, 255, 10, 255, 255, 255,
                   255, 255, 255, 255, 255, 255, 2, 255, 255, 255, 255,
                   5, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                   45, 255, 255, 255, 255, 0, 255, 255, 255, 255, 255,
                   255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                   255, 255, 255, 255, 255, 255, 255, 255, 27, 255, 255,
                   63, 255, 255, 255, 255, 255, 255, 255, 255, 95, 255,
                   0, 255, 41, 255, 255, 255, 255, 255, 255, 255, 255,
                   255, 12, 255, 78, 255, 255, 255, 255, 255, 100, 32],
    }

print(get_pixel(im_1, -1, 12, 'wrap'))
'''
'''
kernel_1 = [0, 0, 0, 0, 1, 0, 0, 0, 1]

kernel = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

'''