#! /usr/bin/env python3
# https://wiki.archlinux.org/index.php/Professional_audio#System_configuration
# http://patorjk.com/software/taag/#p=display&f=Big&t=1%202%203%204
#
# Depends on jack2, opus-tools, ffmpeg, mpv
#
# this script is *nix only (press any key...)

import argparse
import sys
import subprocess
from os.path import exists, join, split, splitext
from os import system
from pprint import pprint
import random
from time import sleep

import shlex # to split CONV


#configure jack
#cat /proc/asound/card0/codec#0 | grep rates | head -n 1
#wiki: /usr/bin/jackd -R -P89 -dalsa -dhw:0 -r48000 -p256 -n3
PROGRAM_NAME = "blindTest"
VERSION      = "0.1"
RATE     = 48000
NPERIODS = 2
PERIOD   = 256

jack_enabled = False
jackproc     = False

#This is used 'as is' just the {} are replaced withthe songs
CONV = [ "opusenc --bitrate 64.0 '{}' '{}'",
         "opusenc --bitrate 128.0 '{}' '{}'",
         "ffmpeg -i '{}' -b:a 128k '{}'",
         "ffmpeg -i '{}' -b:a 196k '{}'"
        ]

def song2opus(song):
    print("Converting: {}".format(song))
    for i,j in enumerate(CONV):
        out="{}-{}.opus".format(splitext(song)[0],i)
        cmd=j.format(song, out)
        if args.debug:
            print(cmd)
        subprocess.run(shlex.split(cmd))

def graphicalJack():
    pass
    # jack_control start
    # jack_control ds alsa
    # jack_control dps device hw:0
    # jack_control dps rate $RATE
    # jack_control dps nperiods $NPERIODS
    # jack_control dps period $PERIOD
    # echo "just a sec..."
    # sleep 5
    # pasuspender -- qjackctl &

def enableJack():
    #
    global jack_enabled, jackproc
    cmd="pasuspender -- /usr/bin/jackd -R -P89 -dalsa -dhw:0 -r{} -p{} -n{}".format(RATE, PERIOD, NPERIODS)
    if args.debug:
        print(cmd)
    jackproc=subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    jack_enabled = True

def disableJack():
    #global jack_enabled, jackproc
    if args.debug:
        print("Disable jack")
    jackproc.terminate()
    jack_enabled = False

def play(order):
    if not args.debug:
        system("clear")
    print("\n  > {} -- can *you* hear the difference?\n\n".format(PROGRAM_NAME))
    for i,j in enumerate(order):
        if j+1>len(CONV):
            j=j-(len(CONV))
            if not jackproc:
                enableJack()
        else:
            if jackproc:
                disableJack()
        sleep(1) #jack is a bit slow... but we don't want to give it away...
        print("Song no: {} (make a note!)".format(i+1))
        cmd = "mpv -ao '{}' --start=1:00 --length=3 '{}-{}.opus'".format(("jack" if jackproc else "pulse"),splitext(args.song)[0], j)
        if args.debug:
            print(cmd)
        subprocess.run(shlex.split(cmd), capture_output=True)
        system('read -p "Press <enter> to continue"')

def showlist(order):
    if jackproc:
        disableJack()
    print("\nThose were all the songs.")
    system('read -p "\nPress <enter> to continue"')
    for i,j in enumerate(order):
        moreJack=""
        if j+1>len(CONV):
            j=j-(len(CONV))
            moreJack="- (played using jack)"
        LINE="- Song no {} encoded with: {} {}".format(i+1, CONV[j], moreJack)
        print(LINE.replace("'{}' ","").replace("-i",""))

def run():
    if args.convert:
        song2opus(args.song)
    playlist_start=len(CONV) if args.jack == 2 else 0 #skip non-jack songs if jack=2
    playlist_length=len(CONV)*(2 if args.jack else 1) #twice as long if jack
    order=list(range(playlist_start,playlist_length))
    random.shuffle(order)
    if args.debug:
        pprint(order)
    play(order)
    showlist(order)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""This script uses mpv for playback,
opusenc and ffmpeg for encoding.

Optionally jackd for real-time audio.
This is not a work of art, just dump all your test music in the same folder...
""")
    parser.add_argument("-c", "--convert", help="Convert song from flac to opus",
                        action="store_true")
    parser.add_argument("-j", "--jack", help="listen using with (and without) jack",
                        action="count")
    parser.add_argument("-d", "--debug", help="enable debugging",
                        action="store_true")
    # parser.add_argument("-s", "--start", help="play song from start-time (eg 1:00)",
    #                    action="store_true")
    # parser.add_argument("-l", "--length", help="how long to play from start-time (eg 1:00)",
    #                    action="store_true")
    parser.add_argument('song', help="Reference song (should probably be .flac)")

    args = parser.parse_args()

    run()
