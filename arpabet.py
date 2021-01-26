import argparse
from itertools import chain

import nltk

# Must uncomment on first run
# nltk.download('cmudict')

def build_parser():
    '''
    Creates an argparse parser
    '''
    parser = argparse.ArgumentParser(description='Adds an Arpabet translation to text files',
                                     prog='srt-parse')

    parser.add_argument('input', type=str,
                        help='Location of file to be processed')
    parser.add_argument('--out-file', type=str,
                        help='Directory for processed files to be saved to',
                        default='./out/out.txt')
    return parser


args = build_parser().parse_args()
arpabet = nltk.corpus.cmudict.dict()

f = open(args.input, "r")
lines = f.readlines()

with open(args.out_file, 'w') as out:
    for idx, line in enumerate(lines):
        sub_line = line.split('|')  # remove the file name before the separator

        new_line = []
        skip = False
        for word in sub_line[-1].split():
            if word not in arpabet:
                skip = True
                break
            new_line += ["{" + " ".join(chain.from_iterable(arpabet[word])) + "}"]
        if skip:
            continue
        out.write(line)
        out.write(sub_line[0] + "|" + " ".join(new_line))

out.close()
