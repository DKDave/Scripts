# Mario Strikers Charged (Wii)
# RESBUN / NLXWB audio extract
# Python script by DKDave, 2024

# For normal DSP files, the .spt table is extracted from the resbun file - rename the .nlxwb file to *.spd and they will play in Foobar/vgmstream
# IDSP files are extracted separately


import os, sys, struct, glob

def read_file(filename, out_folder):
	basename = filename.split(".")[0]
	os.makedirs(out_folder, 0o777, True)

	f = open(filename, "rb")
	data = bytearray(f.read())
	f.close()

	if os.path.exists(basename + ".nlxwb"):
		f2 = open(basename + ".nlxwb", "rb")
	else:
		print(basename + ".nlxwb doesn't exist")
		return

	file_end = os.path.getsize(filename)

	chunk_offset = 8

	while chunk_offset < file_end:
		chunk_type, chunk_size = struct.unpack_from(">II", data, chunk_offset)

		if chunk_type == 0x03023703:								# SPT TABLE
			out_name = basename + ".spt"

			print("Writing:\t" + out_name)

			out = open(out_folder + "\\" + out_name, "wb")
			out.write(data[chunk_offset + 8: chunk_offset + 8 + chunk_size])
			out.close()

		if chunk_type == 0x80023200:								# IDSP table
			temp_offset = chunk_offset + 8

			while temp_offset < (chunk_offset + chunk_size):
				sub_chunk, sub_size = struct.unpack_from(">II", data, temp_offset)

				if sub_chunk == 0x23201:
					idsp_count = struct.unpack_from(">I", data, temp_offset + 8)[0]

				if sub_chunk == 0x23202:
					for a in range(idsp_count):
						idsp_offset, idsp_size = struct.unpack_from(">II", data, temp_offset + 8 + (a * 0x1c) + 4)


						if idsp_size > 0:
							out_name = basename + "_" + str(a) + ".idsp"
							print("Writing:\t" + out_name)

							f2.seek(idsp_offset)
							out = open(out_folder + "\\" + out_name, "wb")
							out.write(f2.read(idsp_size))
							out.close()

				temp_offset += sub_size + 8

		chunk_offset += chunk_size + 8
		chunk_offset += align(chunk_offset, 4)

	f2.close()

	return


def align(offset, value):
	mod = offset % value

	if mod > 0:
		return value - mod
	else:
		return 0



print("================================================================================")
print("Mario Strikers Charged (Wii) audio extractor")
print("Python script by DKDave, 2024")
print("================================================================================\n")

if len(sys.argv) != 2:
	print("Usage: Python resbun.py [output folder]")
	exit()

for filename in glob.glob("*.resbun"):
	read_file(filename, sys.argv[1])


