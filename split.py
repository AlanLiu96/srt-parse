import argparse
import os
import random
import sys
from math import floor


def build_parser():
    '''
    Creates an argparse parser
    '''
    parser = argparse.ArgumentParser(description='Split a file list into a training list and a validation list',
                                     prog='srt-parse')

    parser.add_argument('input', type=str,
                        help='Location of file to be processed')
    parser.add_argument('--output-dir', type=str,
                        help='Directory for processed files to be saved to',
                        default='./out/')
    parser.add_argument('--train-file-name', type=str,
                        help='training file name',
                        default='train.txt')
    parser.add_argument('--val-file-name', type=str,
                        help='validation file name',
                        default='val.txt')
    parser.add_argument('--validation-percentage', type=float,
                        help='Percentage to set as a validation set',
                        default=0.1)
    return parser


parser = build_parser()
args = parser.parse_args()

f = open(args.input, "r")
lines = f.readlines()
num_lines = len(lines)
chosen_lines = set(random.sample(range(num_lines), floor(args.validation_percentage * num_lines)))

try:
    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)
except FileExistsError:
    parser.error(f"Output path {args.output_dir} is not a directory.\nsrt-parse will now exit.")
    sys.exit()

with open(os.path.join(args.output_dir, args.train_file_name), 'w') as train:
    with open(os.path.join(args.output_dir, args.val_file_name), 'w') as val:
        for idx, line in enumerate(lines):
            file = val if idx in chosen_lines else train
            file.write(line)

train.close()
val.close()
