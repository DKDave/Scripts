# ================================================================================
# Nitroplus Blasterz Heroines Infinite Duel (PC)
# Developed by Examu, Published by Nitroplus
# Decompress images from archive and create .bmp files
# Python script by DKDave, 2025
# Last updated: 25 October 2025
# ================================================================================

# Usage: Python nb_dec.py [input archive]
# BMP files will be created for all images in the archive

# Note: some archives are in a different format and don't work yet, as there are no unique identifiers for the files
# Note: the compression method seems to be slightly different for PS3 files, so this will not work for those


import os, sys, struct


# --------------------------------------------------------------------------------
# Decompress image data
# data = compressed image
# --------------------------------------------------------------------------------

def dec(data, width, height):
	new_image = bytearray(width * height)
	in_off = 0
	out_off = 0

	while True:
		if in_off == len(data):
			break

		cw = struct.unpack_from("<H", data, in_off)[0]
		in_off += 2

		for z in range(16):
			if in_off == len(data):
				break

			if cw & 0x8000:								# 1 = copy bytes from further back in output
				cw1 = struct.unpack_from("<H", data, in_off)[0]
				count = ((cw1 & 0xf000) >> 11) + 4					# (top 4 bits * 2) + 4 = number of bytes to copy
				offset = ((cw1 & 0xfff) * 2) + 2						# back reference in output data

				for a in range(count):
					new_image[out_off + a] = new_image[out_off - offset + a]

				in_off += 2
				out_off += count

			else:									# 0 = copy 2 bytes from input
				new_image[out_off] = data[in_off]
				new_image[out_off + 1] = data[in_off + 1]

				in_off += 2
				out_off += 2

			cw <<= 1									# next control bit

	return new_image


# --------------------------------------------------------------------------------
# Main program
# --------------------------------------------------------------------------------

print("================================================================================")
print("Nitroplus Blasterz: Heroines Infinite Duel (PC)")
print("Image decompression")
print("Python script by DKDave, 2025")
print("================================================================================\n")

if len(sys.argv) < 2:
	print("Error:\tNo archive name provided.\n")
	print("Usage:\tPython nb_dec.py [input archive]")
	exit()

in_file = sys.argv[1]											# Input archive

if not os.path.exists(in_file):
	print("Error:\tFilename doesn't exist.  Please try another file.")
	exit()

f = open(in_file, "rb")

codec_names = {0x29: "8-bit + palette", 0x35545844: "DXT5"}

f.seek(0)
width = int.from_bytes(f.read(4), "little")									# Width for all images in archive
height = int.from_bytes(f.read(4), "little")									# Height for all images in archive
codec = int.from_bytes(f.read(4), "little")									# 0x29, "DXT5", etc.
unk2 = int.from_bytes(f.read(4), "little")									# ?
files = int.from_bytes(f.read(4), "little")									# Number of images
unk3 = int.from_bytes(f.read(4), "little")									# ?
pal_data = (files * 12) + 0x18										# Start of palette data

print("Archive:\t" + in_file)
print("Images:\t\t" + str(files))
print("Codec:\t\t" + codec_names[codec] + "\n")

print("------------------------------------------------------------------------------------------")
print(f"{'#':<10}{'Offset':<15}{'Comp size':<15}{'Dec size':<15}{'Dimensions':<20}{'Codec':<20}")
print("------------------------------------------------------------------------------------------\n")

entry = 0x18

for a in range(files):
	f.seek(entry + (a * 12))
	offset = int.from_bytes(f.read(4), "little")
	comp_size = int.from_bytes(f.read(4), "little")
	f.read(4)

	f.seek(offset)
	comp_data = f.read(comp_size)
	dec_data = dec(comp_data, width, height)

	if codec == 0x29:										# 8-bit + palette
		f.seek(pal_data + (a * 1024))
		pal = f.read(0x400)
		bmp_header = struct.pack("<2sIHHIIiiHHIIiiII", b"BM", (width * height) + 1024 + 54, 0, 0, 0x36, 40, width, -height, 1, 8, 0, width * height, 96, 96, 0, 0)

		z = open(in_file + "_" + str(a) + ".bmp", "wb")
		z.write(bmp_header + pal + dec_data)
		z.close()

	elif codec == 0x35545844:									# DXT5
		dds_header = struct.pack("<4sIIIIIII11III4sIIIIIIIIII", b"DDS ", 0x7c, 0x1007, height, width, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x20, 5, b"DXT5", 0, 0, 0, 0, 0, 0x1000, 0, 0, 0, 0)

		z = open(in_file + "_" + str(a) + ".dds", "wb")
		z.write(dds_header + dec_data)
		z.close()

	print(f"{a:<10}{hex(offset):<15}{hex(comp_size):<15}{hex(len(dec_data)):<15}{str(width) + ' x ' + str(height):<20}{codec_names[codec]:<20}")

f.close()

