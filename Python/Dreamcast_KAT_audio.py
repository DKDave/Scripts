# ================================================================================
# Sega Dreamcast
# Extract audio from KAT archives
# Python script by DKDave, 2024
# ================================================================================

# This script will process all KAT archives in the current folder
# Usage:	Python kat.py [output folder]
# Note: Vgmstream can already read the KAT archives, so this is just for extraction purposes

# Tested on the following games:
# Deep Fighter
# Ecco The Dolphin
# Conflict Zone: Modern War Strategy


import os, sys, struct, glob


def read_file(filename, out_folder):
	print("Processing:\t" + filename + "\n")
	basename = filename.split(".")[0]
	os.makedirs(out_folder, 0o777, True)

	codecs = {4: "Yamaha AICA", 8: "PCM 8-bit", 16: "PCM 16-bit"}

	f = open(filename, "rb")
	data = f.read()
	f.close()

	files = struct.unpack_from("<I", data, 0)[0]

	for a in range(files):
		type, offset, size, rate, misc1, bits = struct.unpack_from("<IIIIII", data, (a * 0x2c) + 4)

		if type == 1:								# Type 1 = audio
			audio = data[offset: offset + size]
			filename = basename + "_" + str(a) + ".wav"

			if bits == 4:							# Yamaha AICA
				wav_header = struct.pack("<4sI8sIHHIIHHH4sI", b"RIFF", size + 0x26, b"WAVEfmt ", 0x12, 0x20, 1, rate, rate // 2, 1, 4, 0, b"data", size)

			elif bits == 8:							# PCM8 signed
				wav_header = struct.pack("<4sI8sIHHIIHH4sI", b"RIFF", size + 0x24, b"WAVEfmt ", 0x10, 1, 1, rate, rate, 1, 8, b"data", size)

				audio = bytearray(size)

				for b in range(size):
					audio[b] = (data[offset + b] + 128) & 0xff			# Convert to unsigned

			elif bits == 16:
				wav_header = struct.pack("<4sI8sIHHIIHH4sI", b"RIFF", size + 0x24, b"WAVEfmt ", 0x10, 1, 1, rate, rate * 2, 2, 16, b"data", size)

			else:
				print("Unknown bits:\t", bits)
				return

			out = open(out_folder + "\\" + filename, "wb")
			out.write(wav_header + audio)
			out.close()

			print(f"{'Writing  ... ' + filename:<35}{codecs[bits]:<15}{rate:<10}{str(size) + ' bytes':<20}")

	print("\n")

	return



print("Dreamcast KAT audio extractor")
print("Python script by DKDave, 2024\n")

if len(sys.argv) != 2:
	print("Usage: Python kat.py [output folder]")
	exit()

for filename in glob.glob("*.kat"):
	read_file(filename, sys.argv[1])




