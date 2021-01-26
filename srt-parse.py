import argparse
import os
import sys

import srt
from pydub import AudioSegment


def get_slice_indexes(sub):
    '''
    Returns the indexes used to slice the corresponding audio from the subtitle

    Keyword arguments:
    sub - a srt subtitle
    '''
    return int(sub.start.total_seconds() * 1000), int(sub.end.total_seconds() * 1000)


def build_parser():
    '''
    Creates an argparse parser
    '''
    parser = argparse.ArgumentParser(description='Segment audio files according to a provided .srt closed caption file',
                                     prog='srt-parse')

    parser.add_argument('audio_input', type=str,
                        help='Location of file to be processed (any ffmpeg format files are supported, ex. wav, mp4)')
    parser.add_argument('srt_input', type=str,
                        help='Location of .srt file to be processed')
    parser.add_argument('--output-dir', type=str,
                        help='Directory for processed files to be saved to',
                        default='.\\out\\')
    parser.add_argument('--audio-out-file-pattern', type=str,
                        help='A python-style f-string for saving audio files',
                        default='{}-audio.wav')
    parser.add_argument('--text-out-file-pattern', type=str,
                        help='A python-style f-string for saving text files',
                        default='{}-text.txt')
    parser.add_argument('--output-type', type=str,
                        help='Output filetype',
                        choices=['txt', 'csv'],
                        default='csv')
    parser.add_argument('--csv-separator', type=str,
                        help='Character sequence used to separator values in csv',
                        default='|')
    parser.add_argument('--csv-filename', type=str,
                        help='Name of file to write as csv',
                        default='out.csv')
    parser.add_argument('--update-increment', type=int,
                        help='Print progress after every specified amount of segments.',
                        default=25)
    parser.add_argument('--in-encoding', type=str,
                        help='Encoding used to read the .srt file',
                        default='utf-8')
    parser.add_argument('--out-encoding', type=str,
                        help='Encoding to use when writing text data to file',
                        default=None)
    return parser


def write_txt():
    '''
    Write data in .txt format
    '''
    for idx, sub in enumerate(subs):
        if idx % args.update_increment == 0:
            print(f'Processing segment #{idx}')

        start, end = get_slice_indexes(sub)
        clip = audio[start:end]
        clip.export(args.output_dir + "/wavs/" + args.audio_out_file_pattern.format(idx), format='wav')
        with open(os.path.join(args.output_dir, args.text_out_file_pattern.format(idx)), 'w',
                  encoding=args.out_encoding) as f:
            f.write(sub.content.replace('\n', ' '))


def write_csv():
    '''
    Write data in .csv format

    Subtitles on YouTube are set to last for "two lines", so we need to combine the next line as well.
    '''
    with open(os.path.join(args.output_dir, args.csv_filename), 'w', encoding=args.out_encoding) as f:
        length = len(subs)
        for idx, sub in enumerate(subs):
            if idx + 1 < length - 1:
                sub.content = sub.content + " " + subs[idx + 1].content
            if "[" in sub.content:
                continue  # "naughty" language filter in subs
            if idx % args.update_increment == 0:
                print(f'Processing segment #{idx}')
            start, end = get_slice_indexes(sub)
            clip = audio[start:end]
            clip.export(os.path.join(args.output_dir + "/wavs/", args.audio_out_file_pattern.format(idx)), format='wav')
            f.write(args.csv_separator.join(["wavs/" + args.audio_out_file_pattern.format(idx), sub.content.replace('\n', ' ')]))
            f.write('\n')


def get_write_function():
    '''
    Determine which method to use to write to file.
    '''
    write_map = {'txt': write_txt,
                 'csv': write_csv}
    return write_map[args.output_type]


def get_subs():
    '''
    Returns a generator yielding parsed captions from the .srt
    '''
    with open(args.srt_input, 'r', encoding=args.in_encoding) as f:
        str_sub = ''.join(f.readlines())
    return [sub for sub in srt.parse(str_sub)]


# Get parser and parse
parser = build_parser()
args = parser.parse_args()

# Error checking
if args.update_increment <= 0:
    parser.error("Update increment must be a postive number")

# Check if output path exists and is a directory
try:
    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)
    if not os.path.exists(args.output_dir + "/wavs"):
        os.mkdir(args.output_dir + "/wavs")
except FileExistsError:
    parser.error(f"Output path {args.output_dir} is not a directory.\nsrt-parse will now exit.")
    sys.exit()

# Open srt file
subs = get_subs()

file_extension = args.audio_input.split(".")[-1]
# Open audio file
audio = AudioSegment.from_file(args.audio_input, file_extension)

# Determine which writing function to use
write = get_write_function()

# Process audio clips
write()

print('Processing finished!')
