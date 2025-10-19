# ================================================================================
# Emergency: Fighters For Life (1998)
# CFF / VFF / AFF image decompression
# Python script by DKDave, 2025
# ================================================================================

# This script will read all of the CFF/VFF/AFF compressed image files and output .bmp files
# For VFF and AFF files, a suitable palette file will be loaded - either one with the same name as the base file, or farben.pal
# Usage: Python em.py [CFF/VFF/AFF file]

# CFF = 1 image + palette
# VFF = multiple images, various sizes, external palette
# AFF = multiple images, various sizes, external palette


import os, sys, struct


# Image decompression
# comp = compressed data without header info
# dec_size = uncompressed data size

def dec(comp, dec_size):
	in_off = 0
	out_off = 0

	decomp = bytearray(dec_size)

	while True:
		cbyte = comp[in_off]							# Control byte

		if cbyte == 0:								# CFF / VFF seem to use 0 as end marker, AFF doesn't
			return decomp, in_off + 1

		if out_off == dec_size:
			return decomp, 0

		if cbyte & 0x80:								# Repeat colour
			colour = comp[in_off+1]
			in_off += 2

			for a in range((cbyte & 0x7f) + 1):
				decomp[out_off + a] = colour

			out_off += ((cbyte & 0x7f) + 1)

		else:									# Copy bytes
			for a in range(cbyte):
				decomp[out_off + a] = comp[in_off + a + 1]

			out_off += cbyte
			in_off += cbyte + 1

	return decomp, in_off



# Create bmp file
# Converts 8-bit image to RGBA32

def create_bmp(image, pal, width, height):
	row_size = ((width * 4) + 3) & 0xfffffffc						# account for row padding if required

	bmp_header = struct.pack("<2sIHHIIIiHHIIIIII", b"BM", (row_size * height) + 54, 0, 0, 0, 40, width, -height, 1, 32, 0, width * height * 4, 1, 1, 0, 0)

	bmp_data = bytearray(row_size * height)

	for a in range(height):
		for b in range(width):
			idx = image[(a * width) + b]					# colour index
			pos = (a * row_size) + (b * 4)					# pixel position in final bitmap data

			col = pal[idx * 3: (idx * 3) + 3]					# Read colour value from palette
			bmp_data[pos + 2] = col[0]					# Add colours to final bitmap data
			bmp_data[pos + 1] = col[1]
			bmp_data[pos + 0] = col[2]
			bmp_data[pos + 3] = 0xff					# No alpha

	return bmp_header + bmp_data



print("--------------------------------------------------------------------------------")
print("Emergency (1998) - Image decompression")
print("Python script by DKDave, 2025")
print("--------------------------------------------------------------------------------\n")

if len(sys.argv) < 2:
	print("Invalid command line parameters.  Please provide at least an input image filename.\n")
	print("Usage: Python Emergency.py [CFF/VFF/AFF file]\n")
	print("If an external palette exists with the same main name as the input file, it will be loaded, otherwise farben.pal will be used.")
	print("Please ensure that farben.pal or a suitable palette file exists in the same folder as the image file,\n")
	exit()

in_file = sys.argv[1]
filename = os.path.splitext(in_file)[0]
file_ext = os.path.splitext(in_file)[1]

if not os.path.exists(in_file):
	print("File not found,  Please try another file.")
	exit()

f = open(in_file, "rb")
data = bytearray(f.read())
f.close()


if file_ext == ".cff":
	print("File:\t" + in_file)
	width = struct.unpack_from("<I", data, 0)[0]
	height = struct.unpack_from("<I", data, 4)[0]

	print("Width:\t" + str(width))
	print("Height:\t" + str(height))

	dec_data, in_off = dec(data[8:], width * height)

	pal = data[in_off + 8: in_off + 8 + 0x300]

	for a in range(0x300):
		pal[a] = pal[a] * 4

	final = create_bmp(dec_data, pal, width, height)

	out = open(filename + ".bmp", "wb")
	out.write(final)
	out.close()


if file_ext == ".vff":
	if os.path.exists(filename + ".vfp"):
		p = open(filename + ".vfp", "rb")
		pal = bytearray(p.read())
		p.close()

	elif os.path.exists(filename + ".pal"):
		p = open(filename + ".pal", "rb")
		pal = bytearray(p.read())
		p.close()

	elif os.path.exists("farben.pal"):
		p = open("farben.pal", "rb")
		pal = bytearray(p.read())
		p.close()

	else:
		print("No palette file found.")
		exit()


	for a in range(0x300):
		pal[a] = pal[a] * 4

	vff_type = struct.unpack_from("<B", data, 0)[0]					# 2 = multiple images all of same size, 3 = multiple images of various sizes
	count = struct.unpack_from("<H", data, 1)[0]

	print("File:\t" + in_file, "\t", str(count) + " images\n")

	if vff_type == 2:
		width = struct.unpack_from("<H", data, 3)[0]
		height = struct.unpack_from("<H", data, 5)[0]
		offset = (count * 4) + 7

		print(f"{'No.':<10}{'Width':<15}{'Height':<15}{'BMP Size':<20}")
		print("--------------------------------------------------------------------------------")

		for a in range(count):
			comp_size = struct.unpack_from("<I", data, (a * 4) + 7)[0]

			dec_data, in_off = dec(data[offset: offset + comp_size], width * height)
			final = create_bmp(dec_data, pal, width, height)

			print(f"{str(a):<10}{width:<15}{height:<15}{str(len(final)) + ' bytes':<20}{filename + str(a) + '.bmp':<30}")

			offset += comp_size

			out = open(filename + "_" + str(a) + ".bmp", "wb")
			out.write(final)
			out.close()

	elif vff_type == 3:
		offset = (count * 8) + 3

		print(f"{'No.':<10}{'Width':<15}{'Height':<15}{'BMP Size':<20}")
		print("--------------------------------------------------------------------------------")

		for a in range(count):
			comp_size = struct.unpack_from("<I", data, (a * 8) + 7)[0]
			width = struct.unpack_from("<H", data, (a * 8) + 3)[0]
			height = struct.unpack_from("<H", data, (a * 8) + 5)[0]

			dec_data, in_off = dec(data[offset: offset + comp_size], width * height)
			final = create_bmp(dec_data, pal, width, height)

			print(f"{str(a):<10}{width:<15}{height:<15}{str(len(final)) + ' bytes':<20}{filename + str(a) + '.bmp':<30}")

			offset += comp_size

			out = open(filename + "_" + str(a) + ".bmp", "wb")
			out.write(final)
			out.close()


if file_ext == ".aff":
	if os.path.exists(filename + ".vfp"):
		p = open(filename + ".vfp", "rb")
		pal = bytearray(p.read())
		p.close()

	elif os.path.exists(filename + ".pal"):
		p = open(filename + ".pal", "rb")
		pal = bytearray(p.read())
		p.close()

	elif os.path.exists("farben.pal"):
		p = open("farben.pal", "rb")
		pal = bytearray(p.read())
		p.close()

	else:
		print("No palette file found.")
		exit()

	for a in range(0x300):
		pal[a] = pal[a] * 4

	count = struct.unpack_from("<H", data, 0)[0]

	offset = (count * 0x0e) + 2

	print("File:\t" + in_file, "\t", str(count) + " images\n")

	print(f"{'No.':<10}{'Width':<15}{'Height':<15}{'BMP Size':<20}")
	print("--------------------------------------------------------------------------------")

	for a in range(count):
		width = struct.unpack_from("<H", data, (a * 0x0e) + 6)[0]
		height = struct.unpack_from("<H", data, (a * 0x0e) + 8)[0]
		comp_size = struct.unpack_from("<I", data, (a * 0x0e) + 10)[0]

		dec_data, in_off = dec(data[offset: offset + comp_size], width * height)
		final = create_bmp(dec_data, pal, width, height)

		print(f"{str(a):<10}{width:<15}{height:<15}{str(len(final)) + ' bytes':<20}{filename + str(a) + '.bmp':<30}")

		offset += comp_size

		out = open(filename + "_" + str(a) + ".bmp", "wb")
		out.write(final)
		out.close()


