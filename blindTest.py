#! /usr/bin/env python3
# https://wiki.archlinux.org/index.php/Professional_audio#System_configuration
# http://patorjk.com/software/taag/#p=display&f=Big&t=1%202%203%204
#
# Depends on jack, opusenc, ffmpeg, mpv
#
# this script is *nix only (press any key...)

import argparse
import sys
import subprocess
from time import sleep, strftime
from os import environ
from os.path import exists, join, split, splitext
import os
from pprint import pprint
import random
from time import sleep, strftime

#configure jack
#cat /proc/asound/card0/codec#0 | grep rates | head -n 1
#wiki: /usr/bin/jackd -R -P89 -dalsa -dhw:0 -r48000 -p256 -n3
PROGRAM_NAME = "blindTest"
VERSION      = "0.1"
RATE     = 48000
NPERIODS = 2
PERIOD   = 256

jack_enabled = False

#This is used 'as is' just the {} are replaced withthe songs
CONV = [ "opusenc --bitrate 64.0 '{}' '{}'",
         "opusenc --bitrate 128.0 '{}' '{}'",
         "ffmpeg -i '{}' -b:a 128k '{}'",
         "ffmpeg -i '{}' -b:a 196k '{}'"
        ]

def song2opus(song):
    print("Converting: {}".format(song))
    for i,j in enumerate(CONV):
        out="{}-{}.opus".format(os.path.splitext(song)[0],i)
        print(j.format(song, out))
        subprocess.run(j.format(song, out), shell=True)

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
    global jack_enabled
    CMD="pasuspender -- /usr/bin/jackd -R -P89 -dalsa -dhw:0 -r{} -p{} -n{} > /dev/null 2>&1 &".format(RATE, PERIOD, NPERIODS)
    #print(CMD)
    subprocess.run(CMD, shell=True)
    jack_enabled = True

def disableJack():
    global jack_enabled
    #print("Disable jack")
    subprocess.run("killall jackd", shell=True)
    jack_enabled = False

def play(order):
    os.system("clear")
    print("\n  > {} -- can *you* hear the difference?\n\n".format(PROGRAM_NAME))
    for i,j in enumerate(order):
        if j+1>len(CONV):
            j=j-(len(CONV))
            enableJack()
        sleep(1) #jack is a bit slow... but we don't want to give it away...
        print("Song no: {} (make a note!)".format(i+1))
        CMD ="mpv -ao {} --really-quiet '{}-{}.opus' 2> /dev/null".format(("jack" if jack_enabled else "pulse"),os.path.splitext(args.song)[0], j)
        #print(CMD)
        subprocess.run(CMD, shell=True)
        if jack_enabled:
            disableJack()
        os.system('read -p "Press <enter> to continue"')

def showlist(order):
    print("\nThose were all the songs.")
    os.system('read -p "\nPress <enter> to continue"')
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
    order=list(range(len(CONV)*(2 if args.jack else 1)))
    random.shuffle(order)
    #pprint(order)
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
                        action="store_true")
    # parser.add_argument("-j", "--jack", help="listing using with jack (1) or jack and pulseaudio (2)",
    #                     const=0, nargs="?", type=int, choices=[1, 2])
    # #FIXME 1 and 2!!!
    # parser.add_argument("-s", "--start", help="play song from start-time (eg 1:00)",
    #                    action="store_true")
    # parser.add_argument("-l", "--length", help="how long to play from start-time (eg 1:00)",
    #                    action="store_true")
    parser.add_argument('song', help="Reference song (should probably be .flac)")

    args = parser.parse_args()

    run()
