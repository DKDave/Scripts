# ================================================================================
# Forspoken (PC)
# EARC extract
# Python script by DKDave, 2023
# ================================================================================

# NOTES:

# Tested on Python version 3.9.5
# Requirements: Install LZ4 for Python using "pip install lz4"
# Usage: Python earc.py [earc archive]
# Any existing files will be overwritten


import sys, os, struct, lz4.frame

print("================================================================================")
print("Forspoken - EARC archive extractor")
print("Python script by DKDave, 2023")
print("================================================================================")
print("")


if len(sys.argv) != 2:
	print("Invalid command line arguments.")
	print("Usage: Python earc.py [archive filename]")
	exit()

file1 = open(sys.argv[1], "rb")

file1.seek(0)
check = file1.read(4).decode("ascii")

if check != "CRAF":
	print("Invalid archive file.")
	file1.close()
	exit()

file1.seek(8)
files = int.from_bytes(file1.read(4), "little")
file1.seek(0x10)
table = int.from_bytes(file1.read(4), "little")

file1.seek(table)
toc = file1.read(files * 0x28)

for a in range(files):
	size = struct.unpack_from("<I", toc, (a * 0x28) + 8)[0]
	zsize = struct.unpack_from("<I", toc, (a * 0x28) + 0x0c)[0]
	offset = struct.unpack_from("<Q", toc, (a * 0x28) + 0x18)[0]
	name_off = struct.unpack_from("<I", toc, (a * 0x28) + 0x20)[0]

	filename = b"Forspoken/"								# default output folder
	count = 0

	file1.seek(name_off)

	while True:
		char = file1.read(1)

		if char == b'\x00':
			break

		filename += char
		count += 1

	filename = filename.decode("ascii")

	if zsize > 0:
		print("Extracting ... " + filename)
		folder = os.path.dirname(filename)
		os.makedirs(folder, 0o777, True)

		if zsize == size:
			out_file = open(filename, "wb")
			file1.seek(offset)
			data = file1.read(zsize)
			out_file.write(data)
			out_file.close()
		else:
			file1.seek(offset)
			comp_data = file1.read(zsize)
			dec_data = lz4.frame.decompress(comp_data)
			out_file = open(filename, "wb")
			out_file.write(dec_data)
			out_file.close()

file1.close()

