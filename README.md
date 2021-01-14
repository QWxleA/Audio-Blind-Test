# Audio-Blind-Test
script to try different opus encodings, and listen if you can hear the difference

## Install dependencies and use

    On Arch:

```` sh
pacman -S jack2 opus-tools ffmpeg mpv
````

    Copy one or more flac-files in the same folder as the script, edit the script to setup the conversion settings you want, to convert use:

```` sh
blindTest.py <song> -c
````

    To use jack and pulse for listening, use:

```` sh
blindTest.py <song> -j
````

    To **only** use jack for listening, use:

```` sh
blindTest.py <song> -j
````


## My sound stopped working!

    The script playes around with **jack**, and sometimes it ends up with either jack running or jack is no longer running, but pulse does not restart. To fix this:"

    Kill **jackd**:

```` sh
pkill jackd
````

    To restart **pulse**:

```` sh
systemctl --user restart pulseaudio.socket
````

    Rebooting also helps, but it shouldn't be necessary.
