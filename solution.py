from PIL import Image
import os, os.path
import numpy as np
import math
import sys
import argparse
import glob


def location():
    parse = argparse.ArgumentParser()
    parse.add_argument('--path', help='file with images', type=str)
    return parse.parse_args().path

def return_intersection(hist_1, hist_2):
    minima = np.minimum(hist_1, hist_2)
    intersection = np.true_divide(np.sum(minima), np.sum(hist_2))
    return intersection

def search_for_images(path):
    files = glob.glob(path + '/*')
    pictures = []
    picture_representation = []
    for f in files[:]:
        if f.endswith('.jpg'):
            pictures.append(f)
            picture_representation.append(Image.open(f).convert('L').resize((256, 256)))
    xlabels = []
    for i in range(len(pictures)):
        # print('========='*5)
        hist_1 = np.histogram(list(picture_representation[i].getdata()), bins=255, range=[0, 255])
        for j in range(i + 1, len(pictures)):
            hist_2 = np.histogram(list(picture_representation[j].getdata()), bins=255, range=[0, 255])
            if return_intersection(hist_1[0], hist_2[0]) >= 0.85:
                xlabels.append((pictures[j], pictures[i]))
    return xlabels

if __name__ == '__main__':
    file = location()
    print(search_for_images(file))
