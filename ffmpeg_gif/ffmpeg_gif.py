#!/usr/bin/env python
import subprocess
import tempfile
import sys
import time
import argparse
import tempfile

'''
Create GIFs from video with ffmpeg.
'''

__author__ = 'Jeremy Crafts'
__email__ = 'craftsje@gmail.com'


def init_args():
    parser = argparse.ArgumentParser(description='Create GIFs with ffmpeg.')
    parser.add_argument('--input', '-i', metavar='input file',
                        help='Source video', required=True)
    parser.add_argument('--markin', '-s', metavar='HH:MM:SS.mmm',
                        help='Timestamp to mark in', required=True)
    parser.add_argument('--markout', '-e', metavar='HH:MM:SS.mmm',
                        help='Timestamp to mark out', required=True)
    parser.add_argument('--scale', metavar='width:height',
                        help='Scale output')
    parser.add_argument('--crop', metavar='width:height:x_offset:y_offset',
                        help='Crop the video (before scaling)')
    parser.add_argument('--filter', '-vf', metavar='filter string',
                        help='Additional ffmpeg video filters')
    parser.add_argument('--output', '-o', metavar='output file', required=True)
    return parser.parse_args()


def validate_timestamp(ts):
    h = '0'
    m = '0'
    s = ts
    try:
        if ':' in ts:
            m, s = ts.rsplit(':', 1)
        if ':' in m:
            h, m = m.rsplit(':', 1)
        if ':' in str(h):
            raise ValueError
        if ':' in str(h):
            raise ValueError
        if (int(h) < 0 or
           int(m) < 0 or int(m) > 59 or
           float(s) < 0 or not (float(s) < 60)):
            raise ValueErro

        return float(h)*3600 + float(m)*60 + float(s)
    except ValueError:
        raise ValueError('Invalid timestamp: ' + ts)


def calc_duration(markin, markout):
    '''
    Convert timestamp difference to duration in seconds
    '''
    ti = validate_timestamp(markin)
    to = validate_timestamp(markout)
    td = to - ti
    rounded = '%.3f' % round(td, 3)
    return rounded


def main():
    args = init_args()
    try:
        duration = calc_duration(args.markin, args.markout)
    except ValueError as e:
        print(e)
        sys.exit()
    palette_file = tempfile.NamedTemporaryFile(suffix='.png').name
    filters = []
    if args.crop:
        filters.append('crop=' + args.crop)
    if args.scale:
        filters.append('scale=' + args.scale)
    else:
        filters.append('scale=0:0')
    if args.filter:
        filters.append(args.filter)

    args1 = ['ffmpeg', '-ss', args.markin, '-t', duration,
             '-i', args.input,
             '-vf', ','.join(filters + ['palettegen']),
             '-y', palette_file]

    args2 = ['ffmpeg', '-ss', args.markin, '-t', duration,
             '-i', args.input,
             '-i', palette_file,
             '-lavfi', ','.join(filters) + ' [x]; [x][1:v] paletteuse',
             '-gifflags', '+transdiff', '-y', args.output]

    subprocess.call(args1)
    subprocess.call(args2)

if __name__ == '__main__':
    main()
