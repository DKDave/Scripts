# ================================================================================
# Decode audio from Lucas Arts SAN (Smush) video files
# Python script by DKDave, 2024
# IACT audio decoding adapted from: https://github.com/scummvm/scummvm/blob/master/engines/scumm/smush/smush_player.cpp
# Last updated: 22 March 2024
# ================================================================================

# Decodes the audio from all SAN video files in the current folder and creates playable .wav files

# Currently only supports IACT audio data from the following games:

# Star Wars: Droidworks (1998)
# Jedi Knight: Mysteries Of The Sith (1998)
# Outlaws (1997)



import os, sys, struct, glob


# Decode one audio block

def decode_block(block):
	buffer = bytearray(4096)
	source_off = 0
	out_off = 0

	shift1= struct.unpack_from("<B", block, source_off)[0]					# Shift values for left/right channels
	shift2 = shift1 >> 4
	shift1 &= 0x0f
	source_off += 1

	for a in range(1024):								# 1024 samples per channel in each block
		temp = struct.unpack_from("<b", block, source_off)[0]
		source_off += 1

		if temp == -128:
			sample = struct.unpack_from(">h", block, source_off)[0]
			source_off += 2
		else:
			sample = temp << shift2

			if sample < -32768:
				sample = -32768

			if sample > 32767:
				sample = 32767

		struct.pack_into("<h", buffer, out_off, sample)
		out_off += 2

		temp = struct.unpack_from("<b", block, source_off)[0]
		source_off += 1

		if temp == -128:
			sample = struct.unpack_from(">h", block, source_off)[0]
			source_off += 2
		else:
			sample = temp << shift1

			if sample < -32768:
				sample = -32768

			if sample > 32767:
				sample = 32767

		struct.pack_into("<h", buffer, out_off, sample)
		out_off += 2

	return buffer


def read_file(filename):
	outfile = filename.split(".")[0]
	outfile += ".wav"

	f = open(filename, "rb")
	audio_buffer = bytearray()									# Temporary audio buffer
	final_audio = bytearray()									# Decoded audio
	file_end = os.path.getsize(filename)
	chunk_offset = 8

# Create audio buffer from all IACT audio segments

	while chunk_offset < file_end:
		f.seek(chunk_offset)
		chunk_name = f.read(4).decode("ascii")
		chunk_size = int.from_bytes(f.read(4), "big")
		chunk_end = chunk_offset + 8 + chunk_size
		sub_chunk_offset = f.tell()

		if chunk_name == "AHDR":
			f.seek(chunk_offset + 0x316)
			sample_rate = int.from_bytes(f.read(2), "little")

		if chunk_name == "FRME":
			while sub_chunk_offset < chunk_end:
				f.seek(sub_chunk_offset)
				sub_chunk_name = f.read(4).decode("ascii")
				sub_chunk_size = int.from_bytes(f.read(4), "big")

				if sub_chunk_name == "IACT":
					f.seek(sub_chunk_offset + 0x1a)
					audio_buffer += f.read(sub_chunk_size - 0x12)

				sub_chunk_offset += sub_chunk_size + 8
				sub_chunk_offset += align(sub_chunk_offset, 2)

		chunk_offset += chunk_size + 8


# Decode audio

	if len(audio_buffer) == 0:
		print(filename + " doesn't contain any relevant audio")
		return

	else:
		block_offset = 0

		while block_offset < len(audio_buffer):
			block_size = struct.unpack_from(">H", audio_buffer, block_offset)[0]
			final_audio += decode_block(audio_buffer[block_offset + 2: block_offset + 2 + block_size])
			block_offset += block_size + 2

		wav_header = struct.pack("<4sI8sIHHIIHH4sI", b"RIFF", len(final_audio) + 0x24, b"WAVEfmt ", 0x10, 1, 2, sample_rate, sample_rate * 4, 4, 16, b"data", len(final_audio))

		print("Writing:\t", outfile)

		x = open(outfile, "wb")
		x.write(wav_header + final_audio)
		x.close()

	return


def align(offset, size):
	mod = offset % size

	if mod > 0:
		return size - mod
	else:
		return 0



print("================================================================================")
print("Lucas Arts SAN audio extractor")
print("Python script by DKDave, 2024")
print("================================================================================")
print("")

print("Processing all SAN files in current folder ...")
print("")

for filename in glob.glob("*.san"):
	read_file(filename)



