#
#  cmd.py
#
#  Copyright (c)2022 Shane Ambler <Develop@ShaneWare.biz>
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following disclaimer
#    in the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of the  nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#


import argparse
from os.path import join, exists, expanduser
import signal
import sys

from . import __version__ as vers

def signal_handler(signal, frame):
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGQUIT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGTSTP, signal_handler)


def main():
    parser = argparse.ArgumentParser(description='''Sawsc.''')
    parser.add_argument('--version', action='version', version='%(prog)s v'+vers.__version__)
    parser.add_argument('--debug', help='output debug info', action='store_true')
    parser.add_argument('-c', '--config', help='Config file', type=str, default='./sawc.conf')
    parser.add_argument('-s', '--show', help='Show plan of resources to create or modify', action='store_true')
    parser.add_argument('-w', '--write', help='Send changes to AWS account', action='store_true')
    args = parser.parse_args()

    if args.config:
        print(f'Using config file {args.config}')

    if args.show:
        print('These are the additions and changes...')

    if args.write:
        print('Creating and adjusting resources...')

    return 0

if __name__ == '__main__':
    main()

