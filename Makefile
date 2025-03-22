stls:
	/Applications/FreeCAD.app/Contents/MacOS/FreeCAD -c "exec(open('./export-bodies.py').read())"

output.gif: preview.mp40000-0100.mkv
	ffmpeg -y -i preview.mp40000-0100.mkv -vf "fps=15,scale=640:-1:flags=lanczos,palettegen" palette.png
	ffmpeg -i preview.mp40000-0100.mkv -i palette.png -filter_complex "fps=15,scale=640:-1:flags=lanczos,paletteuse" output.gif

gif: output.gif

.PHONY: stls gif
