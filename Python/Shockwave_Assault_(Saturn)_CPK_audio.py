# ================================================================================
# Shockwave Assault (Sega Saturn, 1996)
# Extract audio from CPK video files
# Python script by DKDave, 2024
# ================================================================================

# All audio from CPK files in the current folder will be extracted
# Audio is saved as playable .wav files


import os, struct, glob


# Read audio data from CPK file

def read_file(file):
	f = open(file, "rb")
	file_size = os.path.getsize(filename)
	out_file = filename.split(".")[0] + ".wav"

	check = f.read(4)

	if check != b'FILM':
		print("Not a valid CPK file")
		return

	data_start = int.from_bytes(f.read(4), "big")
	chunk_offset = 0x10
	audio = bytearray()

	while chunk_offset < data_start:
		f.seek(chunk_offset)
		chunk_type = f.read(4).decode("ascii")
		chunk_size = int.from_bytes(f.read(4), "big")

		if chunk_type == "FDSC":
			f.seek(chunk_offset + 0x15)
			channels = int.from_bytes(f.read(1), "big")
			bits = int.from_bytes(f.read(1), "big")
			f.read(1)
			sample_rate = int.from_bytes(f.read(2), "big")

		elif chunk_type == "STAB":									# File table
			f.seek(chunk_offset + 12)
			blocks = int.from_bytes(f.read(4), "big")

			for a in range(blocks):
				f.seek(chunk_offset + 0x10 + (a * 0x10))
				block_offset = int.from_bytes(f.read(4), "big") + data_start
				block_size = int.from_bytes(f.read(4), "big")
				block_misc = int.from_bytes(f.read(4), "big")				
				block_type = int.from_bytes(f.read(4), "big")

				if block_type == 1:								# Audio block
					f.seek(block_offset)

					if bits == 8:
						temp_buffer = bytearray(f.read(block_size))
						temp_buffer2 = bytearray(block_size)

						if channels == 1:
							for b in range(block_size):
								temp = struct.unpack_from("<b", temp_buffer, b)[0]
								struct.pack_into("<B", temp_buffer2, b, temp + 128)

						elif channels == 2:
							interleave = block_size // 2

							for b in range(interleave):
								temp1 = struct.unpack_from("<b", temp_buffer, b)[0]
								temp2 = struct.unpack_from("<b", temp_buffer, interleave + b)[0]
								struct.pack_into("<BB", temp_buffer2, b * 2, temp1 + 128, temp2 + 128)

						audio += temp_buffer2

					elif bits == 16:
						temp_buffer = bytearray(f.read(block_size))
						temp_buffer2 = bytearray(block_size)

						if channels == 1:
							for b in range(block_size // 2):
								temp = struct.unpack_from(">H", temp_buffer, b * 2)[0]
								struct.pack_into("<H", temp_buffer2, b * 2, temp)

						elif channels == 2:
							interleave = block_size // 2

							for b in range(interleave // 2):
								temp1 = struct.unpack_from(">H", temp_buffer, b * 2)[0]
								temp2 = struct.unpack_from(">H", temp_buffer, interleave + (b * 2))[0]
								struct.pack_into("<HH", temp_buffer2, b * 4, temp1, temp2)

						audio += temp_buffer2

		chunk_offset += chunk_size


	if len(audio) > 0:
		wav_header = struct.pack("<4sI8sIHHIIHH4sI", b"RIFF", len(audio) + 8, b"WAVEfmt ", 0x10, 1, channels, sample_rate, sample_rate * channels * (bits//8), channels * (bits//8), bits, b"data", len(audio))

		print("Writing " + out_file + " (" + str(bits) + " bit, " + str(sample_rate) + " Hz, " + str(channels) + " channels)")

		out = open(out_file, "wb")
		out.write(wav_header + audio)
		out.close()

	else:
		print("No audio data in " + filename)

	return 1



print("================================================================================")
print("Shockwave Assault (Sega Saturn)")
print("CPK audio extractor")
print("Python script by DKDave, 2024")
print("================================================================================")
print("")

print("Processing all CPK files in current folder ...")
print("")

for filename in glob.glob("*.cpk"):
	print(filename)
	read_file(filename)



