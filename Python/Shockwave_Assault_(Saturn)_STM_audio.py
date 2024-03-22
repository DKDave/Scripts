# ================================================================================
# Shockwave Assault (Sega Saturn, 1996)
# Extract audio from STM files
# Python script by DKDave, 2024
# ================================================================================

# All audio from STM files in the current folder will be extracted
# Audio is saved as playable .wav files


import os, struct, glob


# Read audio data from STM file

def read_file(file):
	f = open(file, "rb")
	file_size = os.path.getsize(file)

	for a in range(256):										# Max entries per file
		audio = bytearray()

		f.seek(a * 8)
		offset = int.from_bytes(f.read(4), "big")
		size = int.from_bytes(f.read(4), "big")

		if offset == 0:
			break

		while True:
			f.seek(offset)
			block_type = f.read(4)							# "AUD!" or "VID!"
			block_size = int.from_bytes(f.read(4), "big")

			if block_type == b"\x00\x00\x00\x00":						# No more blocks for this file
				break

			if block_type == b"AUD!":
				audio += f.read(block_size)

			offset += block_size + 8 + align(offset + block_size + 8, 4)

		out_file = file.split(".")[0] + "_" + str(a) + ".wav"						# No filenames stored, so create one

		if len(audio) > 0:
			wav_header = struct.pack("<4sI8sIHHIIHH4sI", b"RIFF", len(audio) + 0x24, b"WAVEfmt ", 0x10, 1, 1, 22050, 22050, 1, 8, b"data", len(audio))

			for b in range(len(audio)):
				temp = struct.unpack_from("<b", audio, b)[0]
				struct.pack_into("<B", audio, b, temp + 128)

			print("Writing " + out_file)

			out = open(out_file, "wb")
			out.write(wav_header + audio)
			out.close()

	return


def align(value, width):
	mod = value % width

	if mod > 0:
		return width - mod
	else:
		return 0



print("================================================================================")
print("Shockwave Assault (Sega Saturn)")
print("STM audio extractor")
print("Python script by DKDave, 2024")
print("================================================================================")
print("")

print("Processing all STM files in current folder ...")
print("")

for filename in glob.glob("*.stm"):
	read_file(filename)

