import pyautogui
from PIL import ImageGrab
import time
import threading

screen_width = pyautogui.size().width
screen_height = pyautogui.size().height
mouse_block_color_tolerance = 20
mouse_block_size = 5
mouse_present = False
mouse_picture_colour = (196, 195, 186)
hexagon_detection_color_tolerance = 18
hexagon_right_side_x_position = None
pixel_colour_change_tolerance = 4
status = 0


def get_mouse_picture_position():
    vertical_position = screen_height - (screen_height * 350/1440)
    horizontal_position = screen_width / 2
    return horizontal_position, vertical_position

def get_pixel_colour(x, y):
    image = ImageGrab.grab(bbox=(x, y, x + 1, y + 1))
    return image.getpixel((0, 0))

def is_mouse_average_block_present():
    global mouse_present  
    mouse_block = ImageGrab.grab(bbox=(
        get_mouse_picture_position()[0] - mouse_block_size, get_mouse_picture_position()[1] - mouse_block_size, get_mouse_picture_position()[0] + mouse_block_size, get_mouse_picture_position()[1] + mouse_block_size))
    colors = [mouse_block.getpixel((x, y)) for x in range(mouse_block.width) for y in range(mouse_block.height)]
    for color in colors:
        if not is_similar_color(color, mouse_picture_colour, mouse_block_color_tolerance):
            mouse_present = False  
            return False
    mouse_present = True  
    return True


def is_similar_color(color1, color2, tolerance):
    return all(abs(c1 - c2) <= tolerance for c1, c2 in zip(color1, color2))

def hexagon_pixel_x_position():
    mouse_picture_coordinates = get_mouse_picture_position()
    half_middle_slice = ImageGrab.grab(bbox=(screen_width/2, mouse_picture_coordinates[1], screen_width, mouse_picture_coordinates[1] + 1))
    mouse_picture_colour = get_pixel_colour(mouse_picture_coordinates[0], mouse_picture_coordinates[1])

    colors = [half_middle_slice.getpixel((x, 0)) for x in range(half_middle_slice.width)]

    # Find the first color that is not similar to mouse_picture_colour
    for i, color in enumerate(colors):
        if not is_similar_color(color, mouse_picture_colour, hexagon_detection_color_tolerance):
            # Find the next color that is similar to mouse_picture_colour
            for j in range(i, len(colors)):
                if is_similar_color(colors[j], mouse_picture_colour, hexagon_detection_color_tolerance):
                    # Find the next color that is not similar to mouse_picture_colour
                    for k in range(j, len(colors)):
                        if not is_similar_color(colors[k], mouse_picture_colour, hexagon_detection_color_tolerance):
                            return (k + screen_width//2)

clicking_thread = None
thread_timeout = 1.16

import time

def check_color_change(x, y):
    global clicking_thread
    clicked = False
    color = get_pixel_colour(x, y)
    start_time = time.time()  # Record the start time

    while not clicked and time.time() - start_time < thread_timeout:  # Add a timeout
        new_color = get_pixel_colour(x, y)
        if not is_similar_color(color, new_color, pixel_colour_change_tolerance):
            pyautogui.click()
            print('Clicked')
            clicked = True
            time.sleep(0.25)
        color = new_color

    clicking_thread = None  # Reset the flag when the thread finishes or times out

while True:       
        #  print the status every half a second
    print(status)
    while not mouse_present:
        is_mouse_average_block_present()
        print("Can't see the mouse picture, waiting for it to appear before continuing...")

    while mouse_present:
        hexagon_right_side_x_position = hexagon_pixel_x_position()
        status = (f"Mouse picture detected, checking for colour change at {hexagon_right_side_x_position, get_mouse_picture_position()[0]}")

        if hexagon_right_side_x_position is not None and clicking_thread is None:
            clicking_thread = threading.Thread(target=check_color_change, args=(hexagon_right_side_x_position, get_mouse_picture_position()[1]))
            clicking_thread.start()
        else:
            status = ("No matching pixel found")
        is_mouse_average_block_present()