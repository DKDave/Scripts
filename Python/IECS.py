# ================================================================================
# "IECS" audio extract (PS2)
# Python script by DKDave, 2023
# ================================================================================

# Many PS2 games use this format to store audio data.  The format often consists of a header file and a raw audio file, although not always with the same extensions.  This script expects both files to be provided, but some games do store them as one combined file which this script won't currently process.
# Audio will be extracted as playable .vag files


import sys, os, struct


# ================================================================================
# Extract vag files from IECs archive
# ================================================================================

# hd = IECS header
# bd = raw audio data
# filename = output file prefix
# folder = output folder, existing files will not be overwritten

def IECS_extract(hd, bd, filename, folder):
	check = struct.unpack_from("<Q", hd, 0)[0]

	if check != 0x5665727353434549:							# "IECSsreV"
		print("Not a valid audio archive")
		return 1

	hd_size = struct.unpack_from("<I", hd, 0x1c)[0]
	bd_size = struct.unpack_from("<I", hd, 0x20)[0]
	prog_off = struct.unpack_from("<I", hd, 0x24)[0]
	sset_off = struct.unpack_from("<I", hd, 0x28)[0]
	smpl_off = struct.unpack_from("<I", hd, 0x2c)[0]
	vagi_off = struct.unpack_from("<I", hd, 0x30)[0]
	vagi_count = struct.unpack_from("<I", hd, vagi_off + 12)[0] + 1
	vagi_table = vagi_off + 0x10

	for a in range(vagi_count):
		entry_off = struct.unpack_from("<I", hd, vagi_table + (a * 4))[0]
		offset = struct.unpack_from("<I", hd, vagi_off + entry_off)[0]
		samp_rate = struct.unpack_from("<H", hd, vagi_off + entry_off + 4)[0]

		if a == (vagi_count - 1):							# Audio size isn't stored, so calculate it from next entry or end of data
			offset2 = len(bd)
		else:
			entry2_off = struct.unpack_from("<I", hd, vagi_table + (a * 4) + 4)[0]
			offset2 = struct.unpack_from("<I", hd, vagi_off + entry2_off)[0]

		size = offset2 - offset

		vag_header = bytearray(0x30)
		struct.pack_into("<I", vag_header, 0, 0x70474156)					# VAGp
		struct.pack_into(">I", vag_header, 4, 4)
		struct.pack_into(">I", vag_header, 0x0c, size)
		struct.pack_into(">I", vag_header, 0x10, samp_rate)

		out_file = folder + "\\" + filename + "_" + str(a) + ".vag"

		if os.path.exists(out_file):
			print(out_file + " already exists.")					# Do nothing if the file already exists
		else:
			print("Writing: ", out_file)
			vag_file = open(out_file, "wb")
			vag_file.write(vag_header + bd[offset:offset+size])
			vag_file.close()

	return 1


print("================================================================================")
print("SCEI audio archive extractor")
print("Python script by DKDave, 2023")
print("================================================================================")
print("")

if len(sys.argv) != 5:
	print("Error:\tNot enough parameters given.")
	print("\nUsage:\tPython IECS.py [hd_file] [bd_file] [output_folder] [output_filename]")
	print("\nNote: Output folder will be created if it doesn't exist, but any existing files will not be overwritten.")
	exit()

if os.path.exists(sys.argv[3]) == False:
	print("Creating folder:\t" + sys.argv[3] + "\n")
	os.makedirs(sys.argv[3])

hd_file = open(sys.argv[1], "rb")
hd_data = bytearray(hd_file.read())
bd_file = open(sys.argv[2], "rb")
bd_data = bytearray(bd_file.read())

hd_file.close()
bd_file.close()

IECS_extract(hd_data, bd_data, sys.argv[4], sys.argv[3])

