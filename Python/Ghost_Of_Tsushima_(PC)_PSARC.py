# ================================================================================
# Ghost Of Tsushima (PC, 2024)
# Decompress .psarc archives
# Tested on Python v3.9.5
# ================================================================================

# Usage: python psarc.py [input file]
# Install python lz4 module if it's not already available: pip install lz4


import os, sys, struct, time, lz4.block


if len(sys.argv) != 2:
	print("Please provide a compressed PSARC file")
	exit()

in_file = sys.argv[1]

if not os.path.exists(in_file):
	print("Input file not found.")
	exit()

f = open(in_file, "rb")

f.seek(8)
files = int.from_bytes(f.read(4), "little")
entry = 0x20
f.seek(0x10)
total_size = int.from_bytes(f.read(8), "little")
out_file = in_file.replace(".psarc", "_dec.psarc")

# If decompressed archive has already been created, don't create it again

if not os.path.exists(out_file):
	print("Decompressing " + str(files) + " blocks")
	print("Total size: " + str(total_size) + " bytes")

	out = open(out_file, "wb")

	time1 = time.time()

	for a in range(files):
		f.seek(entry + 8)
		offset = int.from_bytes(f.read(8), "little")
		size = int.from_bytes(f.read(4), "little")
		zsize = int.from_bytes(f.read(4), "little")
		comp = int.from_bytes(f.read(1), "little")					# 0 = uncompressed, 3 = LZ4, 0xfe = padding bytes

		f.seek(offset)

		if comp == 0:
			data = f.read(zsize)
			out.write(data)

		elif comp == 3:
			data = f.read(zsize)
			dec_data = lz4.block.decompress(data, size)
			out.write(dec_data)

		elif comp == 0xfe:
			out.write(bytearray(size))

		entry += 0x20

	f.close()
	out.close()

	time2 = time.time()
	print("Completed decompression in: " + str(time2 - time1) + " seconds\n")


# Process the uncompressed PSAR file

f = open(out_file, "rb")

f.seek(0x0c)
data_start = int.from_bytes(f.read(4), "big")
dir_size = int.from_bytes(f.read(4), "big")
files = int.from_bytes(f.read(4), "big") - 1
entry = 0x3e									# skip first entry - filename list
curr_folder = os.getcwd()

f.seek(0x34)
size = int.from_bytes(f.read(5), "big")
offset = int.from_bytes(f.read(5), "big")

f.seek(offset)
names = f.read(size).split(b'\x00')
table = []

for a in range(files):
	f.seek(entry + (a * dir_size) + 0x10)
	misc1 = int.from_bytes(f.read(4), "big")
	size = int.from_bytes(f.read(5), "big")
	offset = int.from_bytes(f.read(5), "big")

	table.append([offset, size])

table.sort()

for a in range(files):
	offset = table[a][0]
	size = table[a][1]
	filename = names[a].decode("ascii")

	folder = os.path.dirname(curr_folder + filename)
	os.makedirs(folder, 0o777, True)

	out = open(curr_folder + filename, "wb")
	f.seek(offset)
	out.write(f.read(size))
	out.close()

	print(f"{'Writing: ' + filename:<150}")

f.close()


