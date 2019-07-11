#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import math
import os
import urllib
from io import BytesIO
from pathlib import Path

import geopy.distance
import pandas as pd
from PIL import Image

from app_conf import zoom_px_dict


def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(
        math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return xtile, ytile


def num2deg(xtile, ytile, zoom):
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return lat_deg, lon_deg


def get_bbox(lat_deg, lon_deg, zoom):
    xtile, ytile = deg2num(lat_deg, lon_deg, zoom)
    nw_corn = num2deg(xtile, ytile, zoom)
    sw_corn = num2deg(xtile, ytile + 1, zoom)
    se_corn = num2deg(xtile + 1, ytile + 1, zoom)
    ne_corn = num2deg(xtile + 1, ytile, zoom)
    return [nw_corn, sw_corn, se_corn, ne_corn]


def get_center_tile(lat, lon, zoom):
    xtile, ytile = deg2num(lat, lon, zoom)
    center = num2deg(xtile + 0.5, ytile + 0.5, zoom)
    return center


def calc_distance_between_corners_in_px(lat, lon, zoom):
    bbox = get_bbox(lat, lon, zoom)
    dist_m = geopy.distance.geodesic(bbox[0], bbox[1]).km * 1000
    dist_px = int(dist_m / zoom_px_dict[zoom])
    return dist_px


def calc_shift_dists_in_px(point_coords, zoom):
    lat_p, lon_p = point_coords
    center_coords = get_center_tile(lat_p, lon_p, zoom)
    lat_c, lon_c = center_coords

    dist_px = calc_distance_between_corners_in_px(lat_p, lon_p, zoom)
    mp = 256 / dist_px
    z = zoom_px_dict[zoom]
    m = 1000

    coords_1 = (lat_c, lon_p)
    coords_2 = (lat_c, lon_c)
    if lon_c > lon_p:
        dist_m = geopy.distance.geodesic(coords_1, coords_2).km * m
        shift_x = int(dist_m / z * mp)
    else:
        dist_m = geopy.distance.geodesic(coords_2, coords_1).km * m
        shift_x = -(int(dist_m / z * mp))

    coords_1 = (lat_c, lon_c)
    coords_2 = (lat_p, lon_c)
    if lat_c > lat_p:
        dist_m = geopy.distance.geodesic(coords_1, coords_2).km * m
        shift_y = -(int(dist_m / z * mp))
    else:
        dist_m = geopy.distance.geodesic(coords_2, coords_1).km * m
        shift_y = int(dist_m / z * mp)

    return shift_x, shift_y


def calc_number_tiles(size_fragment):
    tile_size = 256  # const px size
    max_crop_size = tile_size * 2
    if size_fragment < max_crop_size:
        return 3
    else:
        return 3 + 2 * int(size_fragment / max_crop_size)


def get_image_cluster(
        map_url, lat_deg, lon_deg, zoom, size_fragment, cache_dir):
    smurl = r'{0}/{1}/{2}/{3}.png'
    xmin, ymin = deg2num(lat_deg, lon_deg, zoom)
    n_tiles = calc_number_tiles(size_fragment)
    shift = int((n_tiles - 1) / 2)
    cluster = Image.new('RGB', (256 * n_tiles, 256 * n_tiles))
    for xtile in range(xmin - shift, xmin + shift + 1):
        for ytile in range(ymin - shift, ymin + shift + 1):
            try:
                tmp_name = f'{zoom}_{xtile}_{ytile}.jpg'
                pret_path = cache_dir / tmp_name
                if pret_path.exists():
                    with pret_path.open('rb') as tmp_img:
                        img = BytesIO(tmp_img.read())
                else:
                    imgurl = smurl.format(map_url, zoom, xtile, ytile)
                    imgstr = urllib.request.urlopen(imgurl).read()
                    with pret_path.open('wb') as tmp_img:
                        tmp_img.write(imgstr)
                    img = BytesIO(imgstr)
                tile = Image.open(img)
                cluster.paste(tile, box=(
                    (xtile - xmin + shift) * 256,
                    (ytile - ymin + shift) * 256))
            except:
                print('Could not download image.')
                raise
    return cluster


def crop_img(im, shift_x, shift_y, size):
    width, height = im.size
    left = (width - size) / 2 - shift_x
    top = (height - size) / 2 - shift_y
    right = (width + size) / 2 - shift_x
    bottom = (height + size) / 2 - shift_y
    cropped_im = im.crop((left, top, right, bottom))
    return cropped_im


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-url', help='URL your tile server.')
    parser.add_argument('-csv', help='CSV filename with id, lat, lon.')
    parser.add_argument('-sep', help='Your CSV separator.')
    parser.add_argument('-out', help='Dir to out created images.')
    parser.add_argument('-size', type=int, help='Fragment image size value.')
    parser.add_argument('-zoom', type=int, help='Zoom value.')
    args = parser.parse_args()
    missed_valies = []
    if args.csv and args.size and args.zoom:
        return args.url, args.csv, args.sep, args.out, args.size, args.zoom
    else:
        if not args.csv:
            missed_valies.append('url')
        if not args.csv:
            missed_valies.append('csv')
        if not args.csv:
            missed_valies.append('sep')
        if not args.csv:
            missed_valies.append('out')
        if not args.size:
            missed_valies.append('size')
        if not args.zoom:
            missed_valies.append('zoom')
        print(f'Missed arguments: {", ".join(missed_valies)}')
        os.sys.exit()


def main():
    map_url, csv_filename, sep, out_dir, size_fragment, zoom = parse_args()
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    cache_dir = Path(f'{out_dir}_cache')
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    df = pd.read_csv(csv_filename, sep=sep)
    values = df.values
    length = len(values)
    cnt = 1
    for v in values:
        id_, lat, lon = v
        id_ = str(id_)
        shift_x, shift_y = calc_shift_dists_in_px((lat, lon), zoom)
        ic = get_image_cluster(
            map_url, lat, lon, zoom, size_fragment, cache_dir)
        ci = crop_img(ic, shift_x, shift_y, size_fragment)
        fni = f'{id_}.jpg'
        ci.save(f'{out_dir}/{fni}', 'JPEG', quality=100, optimize=True,
                progressive=True)
        print(f'Created image: {fni} for id: {id_}, '
              f'lat: {lat}, lon: {lon}, # {cnt} from {length}')
        cnt += 1
    os.remove(cache_dir)


if __name__ == '__main__':
    main()
