# ================================================================================
# Primal (PS2)
# Extract English audio files from ISO
# Python script by DKDave, 2024
# ================================================================================

# Audio files are extracted as playable .ss2 files in Foobar/vgmstream


import os, sys, struct


# Read TOC0 table

def read_files(iso, toc_data, out_folder):
	t1_count = struct.unpack_from("<II", toc_data, 4)[0]
	table1 = 0x10
	table2 = table1 + (t1_count * 8)
	chan_info = {1: "Mono", 2: "Stereo"}

	os.makedirs(out_folder, 0o777, True)

	for b in range(t1_count):
		offset = ((struct.unpack_from("<I", toc_data, table1 + (b * 8))[0] & 0x00FFFFFF) * 0x800) + base_offset
		misc1 = struct.unpack_from("<B", toc_data, table1 + (b * 8) + 3)[0]
		t2_idx = struct.unpack_from("<H", toc_data, table1 + (b * 8) + 4)[0]
		misc2 = struct.unpack_from("<H", toc_data, table1 + (b * 8) + 6)[0]
		type = struct.unpack_from("<4s", toc_data, table2 + (t2_idx * 0x14) + 8)[0].decode("ascii").replace("\x00", "")
		size = struct.unpack_from("<I", toc_data, table2 + (t2_idx * 0x14) + 4)[0]
		var1, var2, var3, var4 = struct.unpack_from("<HHHH", toc_data, table2 + (t2_idx * 0x14) + 12)

		out_name = out_folder + "\\" + out_folder + "_" + str(b)

		if type == "STR":
			if var1 == 1:							# 1 = English
				out_name += ".ss2"

				if os.path.exists(out_name):
					print(out_name + " already exists.  File will not be overwritten.")

				else:
					iso.seek(offset)
					data = iso.read(size)
					channels = struct.unpack_from("<I", data, 8)[0]
					rate = struct.unpack_from("<I", data, 0x1c)[0]

					ss2_header = struct.pack("<4sIIIIIII4sI", b"SShd", 0x18, 2, rate, channels, 0x1000, 0xFFFFFFFF, 0xFFFFFFFF, b"SSbd", size - 0x800)

					print(f"{'Writing ... ' + out_name:<50}{chan_info[channels]:<15}{str(rate) + ' Hz':<15}{str(size) + ' bytes':<20}")

					out_file = open(out_name, "wb")
					out_file.write(ss2_header + data[0x800:])
					out_file.close()

	return



print("================================================================================")
print("Primal (PS2)")
print("English audio extractor")
print("Python script by DKDave, 2024")
print("================================================================================\n")

if len(sys.argv) != 2:
	print("Error - ISO name not provided\n")
	print("Usage: Python primal.py [iso_name]")
	exit()

iso_name = sys.argv[1]

if not os.path.exists(iso_name):
	print(iso_name + " not found.  Please provide a valid ISO file.")
	exit()

iso = open(iso_name, "rb")

base_offset = 0x1388000

iso.seek(base_offset)

check = iso.read(4)

if check != b"TOCS":
	print("TOC not found.  Please try another ISO.")
	iso.close()
	exit()

toc_count = int.from_bytes(iso.read(4), "little")
main_toc = bytearray(iso.read(toc_count * 0x28))

for a in range(toc_count):
	toc_size = struct.unpack_from("<I", main_toc, a * 0x28)[0]
	toc_offset = (struct.unpack_from("<I", main_toc, a * 0x28 + 4)[0] * 0x800) + base_offset
	toc_name = struct.unpack_from("<32s", main_toc, a * 0x28 + 8)[0].decode("ascii").replace("\x00", "").replace(".group.toc", "")

	iso.seek(toc_offset)
	toc_data = iso.read(toc_size)

	read_files(iso, toc_data, toc_name)

iso.close()


