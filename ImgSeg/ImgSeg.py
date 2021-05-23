import cv2
import random as rand
import numpy as np
import math
import Components as cpts
import time


# generate a random rgb color
def random_color():
    return int(rand.random() * 255), int(rand.random() * 255), int(rand.random() * 255)


# return the difference between pixel intensities
def get_distance(image, x1, y1, x2, y2):
    r = (image[0][y1, x1] - image[0][y2, x2]) ** 2
    g = (image[1][y1, x1] - image[1][y2, x2]) ** 2
    b = (image[2][y1, x1] - image[2][y2, x2]) ** 2
    return math.sqrt(r + g + b)


# create an id for each vertex
def generate_id(x, y, width):
    return y * width + x


# return an edge tuple
def create_edge(image, width, x1, y1, x2, y2):
    weight = get_distance(image, x1, y1, x2, y2)
    return generate_id(x1, y1, width), generate_id(x2, y2, width), weight


# given an image, return a list of edges
def build_graph(image, width, height):
    graph = []

    # Create edges and append to graph list using 4-connected neighborhood
    for y in range(height):
        for x in range(width):
            if x < width - 1:
                graph.append(create_edge(image, width, x, y, x + 1, y))
            if y < height - 1:
                graph.append(create_edge(image, width, x, y, x, y + 1))
            if x < width - 1 and y < height - 1:
                graph.append(create_edge(image, width, x, y, x + 1, y + 1))
            if x < width - 1 and y > 0:
                graph.append(create_edge(image, width, x, y, x + 1, y - 1))

    return graph


# return the edge weight threshold
def get_threshold(k, size):
    return k / size


# segment the sorted graph
def segment(sorted_graph, num_pixels, k):
    # initialize components class
    components = cpts.Components(num_pixels)

    # initialize threshold values
    threshold = [get_threshold(k, 1)] * num_pixels

    for edge in sorted_graph:
        # get vertices and edge weight
        v1 = components.get_parent(edge[0])
        v2 = components.get_parent(edge[1])
        weight = edge[2]

        # if the vertices do not have the same parent
        if v1 != v2:
            # and the the edge weight is <= v1 and v2's threshold value
            if weight <= threshold[v1] and weight <= threshold[v2]:
                # merge the components
                components.merge_comps(v1, v2)
                # set the parent equal to v1's parent
                parent = components.get_parent(v1)
                # add the edge weight to the parent's threshold value
                threshold[parent] = weight + get_threshold(k, components.get_size(parent))

    return components


# merge components that are smaller than the minimum size
def remove_small(components, sorted_graph, minimum_size):
    for edge in sorted_graph:
        v1 = components.get_parent(edge[0])
        v2 = components.get_parent(edge[1])

        if v1 != v2:
            if components.get_size(v1) < minimum_size or components.get_size(v2) < minimum_size:
                components.merge_comps(v1, v2)

    return components


# paint the image according to known segments
def paint_img(components, width, height):
    # create a list of random colors for each possible pixel
    color = [random_color() for i in range(width * height)]

    # create a 2d array to represent the painted image
    painted_img = np.zeros((height, width, 3), np.uint8)

    # for each pixel in the image
    for y in range(height):
        for x in range(width):
            # Calculate the pixel id
            pixel_id = y * width + x
            # Find the parent vertex_id of pixel_id
            parent_id = components.get_parent(pixel_id)
            # Use parent_id as an index in the color array and paint the respective pixel
            painted_img[y, x] = color[parent_id]

    return painted_img


def main():
    # read image and get its shape
    file_name = 'mountains.jpg'
    image = cv2.imread('images/' + file_name)
    height, width, channel = image.shape

    # ================= Segmentation Variables ====================

    s = .8  # Gaussian blur sigma parameter
    k = 600  # Scale of observation (greater k = larger components)
    minimum_size = 10  # Minimum component size (px)

    # =============================================================

    # start timer
    start = time.time()

    # store the image as a 2D float array
    float_image = np.asarray(image, dtype=float)

    # apply a gaussian blur to the image
    gauss_image = cv2.GaussianBlur(float_image, (5, 5), s)

    # split the blurred image into its b, g, r channels
    b, g, r = cv2.split(gauss_image)
    gauss_image = (r, g, b)

    # build the graph
    graph = build_graph(gauss_image, width, height)

    # sort the graph by edge weight in ascending order
    weight = lambda edge: edge[2]
    sorted_graph = sorted(graph, key=weight)

    # segment the sorted graph
    components = segment(sorted_graph, width * height, k)

    # remove small components
    components = remove_small(components, sorted_graph, minimum_size)

    # calculate elapsed time
    elapsed_time = time.time() - start

    # display results
    result = paint_img(components, width, height)
    print('Height x Width (pixels):', height, ' x ', width)
    print('k-value:', k)
    print('Minimum Component Size:', minimum_size, 'px')
    print('Runtime:', elapsed_time, 'Seconds')
    cv2.imshow('Original', image)
    cv2.imshow('Segmented', result)
    cv2.imwrite('results/ImgSeg_' + file_name, result)
    cv2.waitKey(0)


if __name__ == '__main__':
    main()
