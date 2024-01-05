import argparse
import re
import sys
import tempfile
import typing

import audeer


TESTS = [

    (
        r'''
        
        
{t: this Is a  t'itle}


''',
        r'''{t:This Is A T'itle}
'''
    ),
    (
        r'''{t: this Is a Title}''',
        r'''{t:This Is A Title}
'''
    ),
    (
        r'''{t: this Is a Title}
{st:this is the sub-title}

bla bla bla
   bla bla bla   
   i
   

[C]  [F]  [C]
  [C]  [F]  [C]   
  [C]bla b[F]la
[C]  bla b[F]la   

''',
        r'''{t:This Is A Title}
{st:this is the sub-title}

Bla bla bla
   Bla bla bla
   I


[C]  [F]  [C]
  [C]  [F]  [C]
  [C]Bla b[F]la
[C]  Bla b[F]la
'''
    ),

]


RE_TITLE = re.compile(r'{t:(.*?)}')
RE_TRAILING_CHORD = re.compile(r'^(\s*\[.*?\])')
RE_LYRICS = re.compile(r'^(\s*)(.*)$')


def capitalize_lyrics(lines: typing.List[str]):

    for i in range(len(lines)):

        if not lines[i].lstrip() or lines[i].lstrip().startswith('{'):
            continue

        line = lines[i]
        chords = ''
        while match := RE_TRAILING_CHORD.match(line):
            chord = match.group(1)
            line = line[len(chord):]
            chords += chord

        match = RE_LYRICS.match(line)
        if match:
            spaces, lyrics = match.groups()
            spaces = spaces or ''
            lyrics = lyrics or ''
            if lyrics:
                lyrics = lyrics[0].upper() + lyrics[1:]
            lines[i] = chords + spaces + lyrics


def capitalize_title(lines: typing.List[str]):
    def helper(match):
        title = match.group(1).strip()
        tokens = title.split(' ')
        tokens = [t[0].upper() + t[1:] for t in tokens if t]
        title = ' '.join(tokens)
        return '{t:' + title + '}'

    lines[0] = RE_TITLE.sub(helper, lines[0].strip())


def strip_lines(lines: typing.List[str]):

    for i in range(len(lines)):
        lines[i] = lines[i].rstrip()

    while lines and not lines[0].strip():
        lines.pop(0)

    while lines and not lines[-1].strip():
        lines.pop(-1)


def main(args):

    paths = audeer.list_file_names(args.root, filetype='pro')
    for path in paths:
        with open(path, 'r') as fp:
            lines = fp.readlines()
            strip_lines(lines)
            capitalize_title(lines)
            capitalize_lyrics(lines)
            lines = '\n'.join(lines) + '\n'
        with open(path, 'w') as fp:
            fp.writelines(lines)

    return 0


def cli():

    parser = command_line_args()
    args = parser.parse_args()

    if args.root == '':

        with tempfile.TemporaryDirectory() as root:
            args.root = root
            path = audeer.path(root, '~.pro')
            for source, expected in TESTS:
                with open(path, 'w') as fp:
                    fp.write(source)
                main(args)
                with open(path, 'r') as fp:
                    result = fp.read()
                assert result == expected

    else:

        sys.exit(main(args))


def command_line_args():

    parser = argparse.ArgumentParser(
        description='Format ChordPro files',
        epilog='',
    )
    parser.add_argument(
        'root',
        type=str,
        help='Path to root folder (leave empty to run tests)',
    )

    return parser


if __name__ == '__main__':
    cli()
