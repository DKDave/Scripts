# ================================================================================
# Glass Rose (PS2)
# Extract audio from PAD archives
# Python script by DKDave, 2024
# ================================================================================

# All PAD files in the current folder will be processed.  TBL files containing filenames will also be processed if they exist
# Files are saved as playable .ss2 files


import os, sys, struct, glob


def read_file(filename, out_folder):
	print("Processing:\t", filename + "\n")

	basename = filename.split(".")[0]
	tbl_name = basename + ".tbl"
	tbl_exists = os.path.exists(tbl_name)
	base_offset = 0x2000
	entry = 0
	entry2 = 0
	fnum = 0
	chan_info = {1: "Mono", 2: "Stereo"}

	os.makedirs(out_folder, 0o777, True)

	f = open(filename, "rb")
	data = f.read()
	f.close()

	if tbl_exists:
		tbl = open(tbl_name, "rb")
		data2 = tbl.read()
		tbl.close()

	while True:
		offset, size, channels, rate, interleave, unk1 = struct.unpack_from("<IIIIII", data, entry)

		if offset == 0xFFFFFFFF:
			break

		offset = (offset * 0x800) + base_offset

		if tbl_exists == 1:
			name_off = struct.unpack_from("<I", data2, entry2)[0]
			entry2 += 4
			out_name = get_string(data2, name_off)
		else:
			out_name = basename + "_" + str(fnum) + ".ss2"
			fnum += 1

		ss2_header = struct.pack("<4sIIIIIII4sI", b"SShd", 0x18, 2, rate, channels, interleave, 0xFFFFFFFF, 0xFFFFFFFF, b"SSbd", size)

		if os.path.exists(out_folder + "\\" + out_name):
			print(out_name + " already exists - file will not be overwritten.")

		else:
			print(f"{'Writing: ' + out_name:<35}{str(rate) + ' Hz':<15}{chan_info[channels]:<15}{str(size) + ' bytes'}")

			out_file = open(out_folder + "\\" + out_name, "wb")
			out_file.write(ss2_header + data[offset: offset + size])
			out_file.close()

		entry += 0x18

	print("\n")

	return


def get_string(data, offset):
	name = ""
	a = 0

	while True:
		temp = struct.unpack_from("<B", data, offset + a)[0]

		if temp == 0:
			break
		else:
			name += chr(temp)

		a += 1

	return name


print("================================================================================")
print("Glass Rose (PS2) - PAD audio extract")
print("Python script by DKDave, 2024")
print("================================================================================\n")

if len(sys.argv) != 2:
	print("Usage: Python pad.py [output folder]")
	exit()

for filename in glob.glob("*.pad"):
	read_file(filename, sys.argv[1])

