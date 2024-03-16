# ================================================================================
# Corpse Killer: Graveyard Edition (Sega Saturn, 1995)
# Extract audio from SGA videos
# Python script by DKDave, 2024
# ================================================================================

# Audio is mono, 8-bit signed PCM, 22050 Hz
# Audio is saved as playable .wav files
# All audio from SGA files in the current folder will be extracted


import os, struct, glob


def read_file(file):
	f = open(filename, "rb")
	file_size = os.path.getsize(filename)
	out_file = filename.split(".")[0] + ".wav"

	buffer = bytearray()
	offset = 0

	for a in range(file_size // 0x800):
		f.seek(offset + 4)
		buffer += f.read(0x7fc)
		offset += 0x800

	f.close()

	audio = bytearray()
	offset = 0

	while offset < len(buffer):
		block_type = buffer[offset]
		block_size = struct.unpack_from(">H", buffer, offset + 2)[0]

		if block_type == 0xff:							# end of data blocks
			break

		elif block_type == 0xa2:							# audio block
			audio += buffer[offset + 12: offset + 12 + (block_size - 9)]

		offset += block_size + 4


# Convert signed audio to unsigned and write the .wav file

	for a in range(len(audio)):
		temp = struct.unpack_from("<b", audio, a)[0]
		struct.pack_into("<B", audio, a, temp + 128)

	wav_header = struct.pack("<4sI8sIHHIIHH4sI", b"RIFF", len(audio) + 8, b"WAVEfmt ", 0x10, 1, 1, 22050, 22050, 1, 8, b"data", len(audio))

	if len(audio) > 0:
		print("Writing " + out_file)

		out = open(out_file, "wb")
		out.write(wav_header + audio)
		out.close()
	else:
		print("No audio data in " + filename)

	return 1



print("================================================================================")
print("Corpse Killer: Graveyard Edition (Sega Saturn)")
print("SGA audio extractor")
print("Python script by DKDave, 2024")
print("================================================================================")
print("")

print("Processing all SGA files in current folder ...")
print("")

for filename in glob.glob("*.sga"):
	read_file(filename)


