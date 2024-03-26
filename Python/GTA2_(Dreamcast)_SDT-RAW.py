# ================================================================================
# GTA 2 (Sega Dreamcast)
# Extract audio from SDT/RAW archives
# Python script by DKDave, 2024
# ================================================================================

# This script will process all SDT/RAW archives in the current folder
# Usage:	Python sdt.py [output folder]


import os, sys, struct, glob


def read_file(filename, out_folder):
	print("Processing:\t" + filename + "\n")

	basename = filename.lower().split(".")[0]
	rawfile = basename + ".raw"

	os.makedirs(out_folder, 0o777, True)

	f1 = open(filename, "rb")
	f2 = open(rawfile, "rb")
	table = f1.read()
	data = f2.read()
	f1.close()
	f2.close()

	files = len(table) // 0x18

	for a in range(files):
		offset, size, rate, unk1, unk2 = struct.unpack_from("<IIIII", table, a * 0x18)
		wav_header = struct.pack("<4sI8sIHHIIHHH4sI", b"RIFF", size + 0x26, b"WAVEfmt ", 0x12, 0x20, 1, rate, rate // 2, 1, 4, 0, b"data", size)
		outname = basename + "_" + str(a) + ".wav"

		print(f"{'Writing ... ' + filename:<30}{rate:<10}{str(size) + ' bytes':<20}")

		out = open(out_folder + "\\" + outname, "wb")
		out.write(wav_header + data[offset: offset + size])
		out.close()

	print("\n")

	return


print("GTA 2 (Dreamcast) SDT/RAW audio extractor")
print("Python script by DKDave, 2024\n")

if len(sys.argv) != 2:
	print("Usage: Python sdt.py [output folder]")
	exit()

for filename in glob.glob("*.sdt"):
	read_file(filename, sys.argv[1])


