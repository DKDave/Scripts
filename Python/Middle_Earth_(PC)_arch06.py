# ================================================================================
# Middle Earth
# .arch06 archive extract
# Python script by DKDave, 2026
# ================================================================================

# Requirements:
# Place oo2core_6_win64.dll in windows\system32 folder


import os, sys, struct
from ctypes import *


def align(addr, block_size):
	mod = addr % block_size

	if mod == 0:
		return addr
	else:
		return addr + (block_size - mod)


print("=" * 80)
print("Middle Earth archive extractor")
print("Python script by DKDave, 2026")
print("=" * 80 + "\n")

if len(sys.argv) != 3:
	print("Please provide an archive name and output folder.")
	print("Syntax: Python script.py [archive] [output folder]")
	exit()

in_file = sys.argv[1]
out_folder = sys.argv[2]

if not os.path.exists(in_file):
	print(in_file + " does not exist")
	exit()

f = open(in_file, "rb")

check = f.read(4)

if check != b"LTAR":
	print("Invalid file.  Please try another archive")
	f.close()
	exit()

f.seek(8)
names_size = int.from_bytes(f.read(4), "little")
fldr_count = int.from_bytes(f.read(4), "little")
file_count = int.from_bytes(f.read(4), "little")
entry1 = names_size + 0x30
entry2 = entry1 + (file_count * 0x1e)

f.seek(0x30)
name_text = f.read(names_size)
file_table = f.read(file_count * 0x1e)
dir_info = f.read(fldr_count * 0x10)

fnum = 0

for d in range(fldr_count):
	name_off, unk1, unk2, files = struct.unpack_from("<IIII", dir_info, d * 0x10)

	folder_name = ""
	count = 0

	while True:
		char = struct.unpack_from("<B", name_text, name_off + count)[0]

		if char == 0: break
		else: folder_name += chr(char)

		count += 1

	if files > 0:
		for a in range(files):
			name_off, offset, total_zsize, total_size, unk1 = struct.unpack_from("<IQQQH", file_table, fnum * 0x1e)

			filename = ""
			count = 0

			while True:
				char = struct.unpack_from("<B", name_text, name_off + count)[0]

				if char == 0: break
				else: filename += chr(char)

				count += 1

			f.seek(offset)
			data = f.read(total_zsize)

			out_name = out_folder + "\\" + folder_name + "\\" + filename

# Decompressed and combine compressed parts

			comp_off = 0
			out_buffer = bytearray(total_size)
			out_off = 0

			while out_off < total_size:
				block_zsize, block_size = struct.unpack_from("<II", data, comp_off)
				dec_buffer = bytes(block_size)
				comp_block = data[comp_off + 8: comp_off + 8 + block_zsize]

				if block_zsize == block_size:
					out_buffer[out_off: out_off + block_size] = comp_block[0:]
				else:
					test = windll.oo2core_6_win64.OodleLZ_Decompress(c_char_p(comp_block), c_int(block_zsize), c_char_p(dec_buffer), c_int(block_size), c_int(0), c_int(0), c_int(0), c_int(0), c_int(0), c_int(0), c_int(0), c_int(0), c_int(0), c_int(3))

					out_buffer[out_off: out_off + block_size] = dec_buffer[0:]

				comp_off = align(comp_off + 8 + block_zsize, 4)

				out_off += block_size


# complete file is now decompressed
# If an EMBB archive, extract the files from it instead of just saving the archive
# Do we need the small ".bndl" files ?

			if ".embb" in out_name:
				embb_text_size, embb_files = struct.unpack_from("<II", out_buffer, 8)
				embb_names = out_buffer[0x10: embb_text_size + 0x10]
				embb_name_offs = embb_text_size + 0x10
				embb_offset = embb_name_offs + (embb_files * 4)

				for c in range(embb_files):
					filename2 = ""
					count = 0
					name_off = struct.unpack_from("<I", out_buffer, embb_name_offs + (c * 4))[0]
					embb_size = struct.unpack_from("<I", out_buffer, embb_offset)[0]

					while True:
						char = struct.unpack_from("<B", embb_names, name_off + count)[0]

						if char == 0: break
						else: filename2 += chr(char)

						count += 1

					out_folder2 = os.path.dirname(filename2)
					out_name = out_folder + "\\" + filename2

					print("Writing: " + out_name + " " + str(embb_size) + " bytes")

					os.makedirs(out_folder + "\\" + out_folder2, 0o777, True)
					x = open(out_name, "wb")
					x.write(out_buffer[embb_offset + 4: embb_offset + 4 + embb_size])
					x.close()

					embb_offset += embb_size + 4

			fnum += 1

f.close()


