# ================================================================================
# Lord Of The Rings: Return Of The King (PC)
# Decompress and extract pac files
# Python script by DKDave, 2023
# ================================================================================

# NOTES:
# Please ensure that all 3 data_*.pac files are in the same folder


import os, sys, struct, zlib


# --------------------------------------------------------------------------------
# Read null-terminated text from current file location
# --------------------------------------------------------------------------------

def ReadText(f):
	text = ""

	while True:
		char = f.read(1)

		if char == b'\x00':
			break
		else:
			text += char.decode("ascii")

	return text


# --------------------------------------------------------------------------------
# Main program
# --------------------------------------------------------------------------------

files = ["data_1.pac", "data_2.pac", "data_3.pac"]
out_file = "data_dec.pac"

out = open(out_file, "wb")

for a in range(3):
	file1 = open(files[a], "rb")
	file_end = os.path.getsize(files[a])
	offset = 0x81

	print("Decompressing archive ... ", files[a])

	while True:
		file1.seek(offset)
		size = int.from_bytes(file1.read(4), "little")

		if size == 0 or offset == file_end:
			file1.close()
			break

		zsize = int.from_bytes(file1.read(4), "little")
		data = file1.read(zsize)

		if zsize == size:
			out.write(data)
		else:
			dec_data = zlib.decompress(data)
			out.write(dec_data)

		offset += zsize + 8

out.close()


# Decompressed data should now be in "data_dec.pac" ready for extraction

file1 = open(out_file, "rb")

count = int.from_bytes(file1.read(4), "little")


# Data start offset not stored, so need to calculate it first

for a in range(count):
	filename = ReadText(file1)
	file1.seek(12, 1)

offset = file1.tell()

entry = 4
out_folder = "out\\"

for a in range(count):
	file1.seek(entry)
	filename = ReadText(file1)
	file1.seek(8, 1)
	folder = os.path.dirname(filename)
	size = int.from_bytes(file1.read(4), "little")
	entry = file1.tell()

	if size > 0:
		file1.seek(offset)
		data = file1.read(size)

		print("Writing file ... " + filename)

		os.makedirs(out_folder + folder, 0o777, True)
		out = open(out_folder + filename, "wb")
		out.write(data)
		out.close()

		offset += size

file1.close()

os.remove(out_file)									# delete temporary file


