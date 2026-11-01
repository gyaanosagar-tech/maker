#!/usr/bin/env bash
# Reproduce EP_RANK_01 from the sources listed below.
# Every source is reusable (CC BY 4.0 or CC BY 2.0). Attribution is on screen.
set -e
FF=${FFMPEG:-ffmpeg}

# 1. sources
[ -f assets/jordan.mp4 ] || curl -sL -o assets/jordan.mp4 \
  "https://archive.org/download/youtube-eFa3zdRX58I/eFa3zdRX58I.mp4"
[ -f assets/skate.webm ] || curl -sL -o assets/skate.webm \
  "https://upload.wikimedia.org/wikipedia/commons/e/eb/Skateboarding_at_Mexico_City_-_Flip_-_040.webm"
[ -f assets/pk.ogv ] || curl -sL -o assets/pk.ogv \
  "https://upload.wikimedia.org/wikipedia/commons/0/03/Keller_saves_PK_attempt_by_Henry.ogv"

# 2. shots: letterbox into 9:16 over a blurred fill so nothing is cut away
cut () {  # src ss dur outdir slower xoff
  rm -rf "$4"; mkdir -p "$4"
  $FF -v error -ss "$2" -t "$3" -i "$1" -filter_complex \
    "$( [ "$5" != "1.0" ] && echo "setpts=$5*PTS," )crop=ih*3/4:ih:(iw-ih*3/4)*$6:0,scale=1080:1440,split[bg][fg];\
[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=30,eq=brightness=-0.28:saturation=0.75[b];\
[b][fg]overlay=0:240[o]" \
    -map "[o]" -r 30 -q:v 2 "$4/f%05d.jpg"
}
cut assets/skate.webm   0    1.7 shots/C 2.3  0.5
cut assets/pk.ogv       4.6  4.0 shots/D 1.0  0.5
cut assets/jordan.mp4   3.9  2.4 shots/A 1.0  0.5
cut assets/jordan.mp4  46.5  4.2 shots/B 1.0  0.45

# 3. compose + bursts
python3 build_frames.py

# 4. voice, then master
$FF -y -i assets/n1.mp3 -i assets/n2.mp3 -i assets/n3.mp3 -i assets/n4.mp3 \
  -filter_complex "[0:a]adelay=150|150[a1];[1:a]adelay=3850|3850[a2];[2:a]adelay=7850|7850[a3];[3:a]adelay=10250|10250[a4];\
[a1][a2][a3][a4]amix=inputs=4:normalize=0:duration=longest:dropout_transition=0[m]" \
  -map "[m]" -ar 48000 -ac 2 assets/voice.wav

DUR=$($FF -i base.mp4 -f null - 2>&1 | grep -o "time=[0-9:.]*" | tail -1 | cut -d= -f2)
$FF -y -i base.mp4 -i assets/voice.wav -stream_loop -1 -i ../burst/assets/bed.wav \
  -filter_complex "[1:a]highpass=f=90,acompressor=threshold=-18dB:ratio=3:attack=8:release=140,volume=1.6[vo];\
[2:a]volume=0.16,atrim=0:14.768[bd];[0:a][vo][bd]amix=inputs=3:normalize=0:duration=first[m]" \
  -map 0:v -map "[m]" -c:v copy -c:a aac -b:a 192k -t 14.768 mix.mp4

$FF -y -i mix.mp4 -c:v copy -c:a aac -b:a 192k -movflags +faststart EP_RANK_01.mp4
echo "wrote EP_RANK_01.mp4"
