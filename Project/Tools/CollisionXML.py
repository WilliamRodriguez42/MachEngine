from PIL import Image
from lxml import etree
import glob
import os
import sys
import ntpath

"""
This program takes in a path to a folder that contains a set of PNG images. These images contain colored rectangles that
represent collision boxes. This program takes those images, finds the location of all of the rectangles, and makes an XML file
with elements that represent each image, and sub-elements that represents each box. This XML allows for faster loading of
collisions at runtime.

ASSUMPTIONS:
    The images are in PNG format and are named by integers, which represent which frame in the texture atlas it matches up with
    The images are named 0000.png, 0001.png, 0002.png and so on
    The center of these images represent the center of the subimage on the texture atlas
                (ie. the origin of both images is in the center)
    The images are in RGBA format
    Each rectangle in the image is a different color
"""

def Decode(filepath):

    image_names = glob.glob(os.path.join(filepath, '*.png')) # Grab a list of all png's in this path

    if len(image_names) == 0: # If there are no png's then print an error
        print('You must specify a folder with png images within it')
        return

    # Make a root element for our XML
    root = etree.Element('Boxes')

    # Loop through each image
    for image_name in image_names:
        _, name = ntpath.split(image_name) # Get the name of the image from the filepath
        name = int(name[:-4]) # Remove the last

        im = Image.open(image_name, 'r').convert('RGBA') # Convert to RGBA if the image is not in 8888 format
        pix = im.load()

        child = etree.SubElement(root, 'S' + str(name)) # Create a child to represent the image

        # Store the width and height of the image (This is important for scaling images in-game)
        width, height = im.size
        child.attrib['pw'] = str(width)
        child.attrib['ph'] = str(height)

        # I iterates through the columns, J iterates through the rows
        # The point of the following variables is to grab the value of I, J that is closest and farthest from the origin
        # (The origin of PIL images is in the top left corner)

        nearestI = 0
        nearestJ = 0
        farthestI = width
        farthestJ = height

        existing_colors = []

        # Get the center of the image (used for converting the origin from top-left to center)
        centerx = width / 2
        centery = height / 2

        counter = 0 # A counter (for naming purposes)

        # Search for the boxes
        for j in range(height):
            for i in range(width):
                color = pix[i, j]
                if color[3] != 0 and color not in existing_colors: # If the color is opaque grab the box (Also don't look for colors that we've already found)

                    # Find the nearest and farthest I of the box
                    nearestI = i
                    for fi in range(i, width):
                        if pix[fi, j] != color:
                            break
                    farthestI = fi

                    # Find the nearest and farthest J of the box
                    nearestJ = j
                    for fj in range(j, height):
                        if pix[i, fj] != color:
                            break
                    farthestJ = fj

                    # Convert nearest and farthest values from pixels to floats on the range [0, 1]
                    nearestI = (nearestI - centerx) / width
                    nearestJ = (nearestJ + centery) / height
                    farthestI = (farthestI - centerx) / width
                    farthestJ = (farthestJ + centery) / height

                    # Rename some of the variables and flip the y-axis
                    fx = farthestI
                    fy = 1 - nearestJ
                    nx = nearestI
                    ny = 1 - farthestJ

                    # Get the center of the box (for convenience when making the game)
                    cx = (nx + fx) / 2
                    cy = (ny + fy) / 2

                    # Store everything into the XML node
                    hit_element = etree.SubElement(child, 'B' + str(counter))
                    hit_element.attrib['fx'] = str(fx)
                    hit_element.attrib['fy'] = str(fy)
                    hit_element.attrib['nx'] = str(nx)
                    hit_element.attrib['ny'] = str(ny)
                    hit_element.attrib['cx'] = str(cx)
                    hit_element.attrib['cy'] = str(cy)

                    # Store the color (It's easier to render and identify the box this way)
                    # Also, convert the color to floats on the range [0, 1] (OpenGL doesn't use 0-255)
                    my_color = [p / 255 for p in color]
                    hit_element.attrib['r'] = str(my_color[0])
                    hit_element.attrib['g'] = str(my_color[1])
                    hit_element.attrib['b'] = str(my_color[2])

                    counter += 1

                    # Record this color so that we don't look for this box again
                    existing_colors.append(color)

    # Save the XML
    content = etree.tostring(root, pretty_print=True)

    file = open(os.path.join(filepath, 'Collision.xml'), 'w+')
    file.write(content.decode('UTF-8'))
    file.close()

if __name__ == '__main__':
    if len(sys.argv) == 2:
        Decode(sys.argv[1])
    else: # If there are excess arguments or too few arguments, warn the user
        print("You need to enter 1 argument: a folder with png files")
