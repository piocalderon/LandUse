# -*- coding: utf-8 -*-
"""
Created on Sun Jul 06 22:39:01 2014

@author: Pio Calderon
"""

import numpy as np
import os
import Image
from itertools import permutations
from skimage.measure import find_contours
from shapely.geometry import Polygon, Point
import matplotlib.pyplot as plt
from descartes.patch import PolygonPatch


def extract_regions(filepath):
    """
    Extracts the habitable regions from filepath and returns the (x,y)
    coords in a list.
    """   
    img = pad_image(filepath)
    img_as_array = np.array(img.convert('L').rotate(180)\
        .transpose(Image.FLIP_LEFT_RIGHT))
            
    # x and y are inverted
    inv_regions = find_contours(img_as_array, 0.5)

    # boundary of image itself
    map_boundary = Polygon([(x,y) for y, x in inv_regions[0]])    
    
    # container for corrected (x, y)'s
    regions = []
    region_polygons = []
    
    # loop to reverse each (x, y)
    for region in inv_regions[1:]:        
        current = []        
        for y, x in region:
            current.append((x, y))  
        intersected = map_boundary.intersection(Polygon(current))  
        
        try:
            regions.append(intersected.boundary.coords)

        except AttributeError:
            print type(intersected)
            print "error in " + os.path.split(filepath)[1][:-4]
            for i in intersected:
                print type(i)
        region_polygons.append(intersected)
        
    fig = plt.figure(figsize = (10, 10), facecolor = "black")
    ax = fig.add_subplot(111)#fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0,1300)
    ax.set_ylim(0,1300)    
    patch = PolygonPatch(intersected, fc = "none", ec = "green",\
                aa=False)
    ax.add_patch(patch)

    plt.savefig(filepath[:-4] + "outline.png")
    plt.close()
    
    interior = set()
    region_index_permutations = permutations(xrange(len(regions)), 2)
    for i, j in region_index_permutations:
        if region_polygons[i].contains(region_polygons[j]):
            interior.add(j)

    interior = list(interior)
    interior.sort()
    interior.reverse()

#    region_boundary = Polygon(regions[0])
#    fig = plt.figure(figsize = (10, 10), facecolor = "black")
#    ax = fig.add_subplot(111)#fig.add_axes([0, 0, 1, 1])
#    patch = PolygonPatch(region_boundary, fc = "red", ec = "green",\
#                aa=False)
#    ax.add_patch(patch)
#    plt.plot()

    print "#regions: " + str(len(regions))
    return regions, interior, img.size
    
def extract_samples(samplepath, regions):
    """
    Extract samples from samplepath and group them (in lists) according
    to their region of membership.
    """    
    sample_img = pad_image(samplepath)
    sample_as_array = np.array(sample_img.convert('L').rotate(180)\
        .transpose(Image.FLIP_LEFT_RIGHT))

    region_polygons = []
    for region in regions:
        region_polygons.append(Polygon(region))
    
    samples = np.nonzero(sample_as_array[2:-2, 2:-2])
    samples = zip(samples[1], samples[0])
    
#    samples = [(x, y) for x in xrange(int(sample_as_array.shape[0])) \
#        for y in xrange(int(sample_as_array.shape[1])) if \
#        sample_as_array[x, y] != 0]

    sorted_samples = dict()
    for index in xrange(len(region_polygons)):
        sorted_samples[index] = []
    
    for sample in samples:
        for index, region_polygon in enumerate(region_polygons):
            if region_polygon.contains(Point(sample)):
                sorted_samples[index].append(sample)
                break

    return sorted_samples
    
def pad_image(imgpath):
    img = Image.open(imgpath)
    img_as_array = np.array(img.convert('L'), dtype = int)
    width, height = int(img_as_array.shape[0]), int(img_as_array.shape[1])
    padded = np.ones((width + 4, height + 4))
    padded.fill(255)
    padded[1:-1, 1:-1] = 0
    padded[2:-2, 2:-2] = img_as_array
    img = Image.fromarray(padded).convert('RGB')
    return img
    
def randomly_sample(imgpath, number):
    img = Image.open(imgpath)
    w, h = img.size
    sampled = Image.new("L", (w,h))
    
    count = 0
    while count < number:
        sampled.putpixel((np.random.random_integers(0, w - 1), np.random.random_integers(0, h - 1)), 255)
        count += 1
        
    head, tail = os.path.split(imgpath)
    sampled.save(head + "\\sample_" + tail)

if __name__ == "__main__":    
    randomly_sample("visayas.png", 5000)
    
    
# error is in extract_regions part na may intersect with map_boundary
# for 1- sample areas, do not voronoi anymore. yun na mismo.
# for 2- sample area, think of a solution