# ================================================================================
# Cyberia 1 (PC)
# Extract audio from .C93 files
# Python script by DKDave, 2024
# ================================================================================

# Usage:
# Python Cyberia_(PC)_C93.py

# All .C93 files in current folder will be processed


import os, sys, struct, glob


def read_file(name):
	f = open(name, "rb")
	data = f.read()
	f.close()

	out_file = name.replace(".C93", ".wav")
	audio_offset = 0
	audio_data = bytes()

	while True:
		audio_offset = data.find(b"Creative", audio_offset + 1)

		if audio_offset == -1:
			break
		else:
			audio_size = struct.unpack_from("<H", data, audio_offset + 0x1b)[0] + (struct.unpack_from("<B", data, audio_offset + 0x1d)[0] * 65536)
			audio_data += data[audio_offset + 0x20: audio_offset + 0x20 + audio_size - 2]

	if len(audio_data) > 0:
		wav_header = struct.pack("<4sI8sIHHIIHH4sI", b"RIFF", len(audio_data) + 8, b"WAVEfmt ", 0x10, 1, 1, 16129, 16129, 1, 8, b"data", len(audio_data))

		print("Writing ... " + out_file)

		f2 = open(out_file, "wb")
		f2.write(wav_header + audio_data)
		f2.close
	else:
		print("No audio data in ... " + name)

	return


print("Cyberia PC /C93 audio extractor")
print("Python script by DKDave, 2024\n")

for filename in glob.glob("*.c93"):
	read_file(filename)


