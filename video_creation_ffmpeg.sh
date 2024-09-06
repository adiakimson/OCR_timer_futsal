# Sample bash script for ffmpeg video creation just use it to "create" sample timer
echo "Running script..."
ffmpeg -f lavfi -i color=c=black:s=640x480:d=60 -vf "drawtext=fontfile=/path/to/font.ttf: \
fontsize=72: fontcolor=white: x=(w-text_w)/2: y=(h-text_h)/2: \
text='%{eif\:1200-t\:d\:2}:%{eif\:(59-t%60)\:d\:2}': \
r=25" output.mp4
echo "Finished, saved in same folder the script is."