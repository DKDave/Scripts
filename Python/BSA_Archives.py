# ================================================================================
# BSA archive extract (Fallout 3, Oblivion)
# Python script by DKDave, 2023
# ================================================================================


import os, sys, struct, zlib

print("================================================================================")
print("BSA archive extractor")
print("Python script by DKDave, 2023")
print("================================================================================\n")

if len(sys.argv) != 2:
	print("Incorrect number of parameters.  Please use: Python bsa.py [bsa file]")
	exit()

file1 = open(sys.argv[1], "rb")

file1.seek(0)
check = file1.read(4)

if check != b'BSA\x00':
	print("Not a BSA file.")
	file1.close()
	exit()

file1.seek(8)
table1 = int.from_bytes(file1.read(4), "little")
file1.seek(4, 1)
folder_count = int.from_bytes(file1.read(4), "little")
file1.seek(0x1c)
names_size = int.from_bytes(file1.read(4), "little")


for a in range(folder_count):
	file1.seek(table1 + (a * 0x10) + 8)
	file_count = int.from_bytes(file1.read(4), "little")
	folder_offset = int.from_bytes(file1.read(4), "little") - names_size

	file1.seek(folder_offset)
	len = int.from_bytes(file1.read(1), "little")
	folder_name = file1.read(len).decode("ascii").replace("\x00", "")
	folder_table = file1.tell()

	for b in range(file_count):
		file1.seek(folder_table + (b * 0x10) + 8)
		zsize = int.from_bytes(file1.read(4), "little")
		offset = int.from_bytes(file1.read(4), "little")
		flag = (zsize & 0x40000000) >> 30
		zsize = zsize & 0x3FFFFFFF

		if a == 0 and b == 0:								# Calculate name text table
			name_text = offset - names_size

		file1.seek(name_text)
		filename = ""

		while True:
			char = file1.read(1)
			if char == b'\x00':
				break
			else:
				filename += char.decode("ascii")

		name_text = file1.tell()							# Save position of next string

		file1.seek(offset)

		if flag == 0:
			data = file1.read(zsize)
		else:
			size = int.from_bytes(file1.read(4), "little")
			comp_data = file1.read(zsize - 4)
			data = zlib.decompress(comp_data)

		print("Writing file ... " + folder_name + "\\" + filename)

		os.makedirs("out\\" + folder_name, 0o777, True)
		out_file = open("out\\" + folder_name + "\\" + filename, "wb")
		out_file.write(data)
		out_file.close()

file1.close()

