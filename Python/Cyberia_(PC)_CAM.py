# ================================================================================
# Cyberia 1 (PC)
# Extract audio from CAM files
# Python script by DKDave, 2024
# ================================================================================

# Usage:
# Python Cyberia_(PC)_CAM.py

# All CAM files in current folder will be processed


import os, sys, struct, glob


def read_file(name):
	f = open(name, "rb")
	data = f.read()
	f.close()

	basename = os.path.basename(filename)

	audio_offset = struct.unpack_from("<I", data, 4)[0]
	check = struct.unpack_from("<I", data, audio_offset)[0]

	if check == 0:
		print("No audio data in " + name)
		return

	offsets = struct.unpack_from("<%dI" %check, data, audio_offset)

	files = (check - 4) // 4

	for a in range(files):
		start = offsets[a] + audio_offset
		audio_size = struct.unpack_from("<H", data, start + 0x1b)[0] + (struct.unpack_from("<B", data, start + 0x1d)[0] * 65536) - 2
		rate = struct.unpack_from("<B", data, start + 0x1e)[0]
		rate = 1000000 // (256 - rate)
		type = struct.unpack_from("<B", data, start + 0x1f)[0]

		wav_header = struct.pack("<4sI8sIHHIIHH4sI", b"RIFF", audio_size + 8, b"WAVEfmt ", 0x10, 1, 1, rate, rate, 1, 8, b"data", audio_size)
		out_file = basename + "_" + str(a) + ".wav"

		print("Writing ..." + out_file)

		f2 = open(out_file, "wb")
		f2.write(wav_header + data[start + 0x20: start + 0x20 + audio_size])
		f2.close

	return


print("Cyberia PC CAM audio extractor")
print("Python script by DKDave, 2024\n")

for filename in glob.glob("cam???"):
	read_file(filename)


