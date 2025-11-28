# ================================================================================
# Nitroplus Blasterz: Heroines Infinite Duel (PS3)
# Developed by Examu, Published by Nitroplus
# Decompress images from .PIL/.ITD archives
# Python script by DKDave, 2025
# ================================================================================

# Usage: Python [script name].py [PIL archive]


# Notes:

# This script only works on .PIL files in the ITD folder for now.
# Images are saved as .png files to save space

# TO DO:

# Correctly rearrange the picture segments to create the correct images
# Process the DXT images



import os, sys, struct, zlib


# --------------------------------------------------------------------------------
# Decompress image data
# data = compressed image
# --------------------------------------------------------------------------------

def dec(data, dec_size):
	new_image = bytearray(dec_size)
	in_off = 0
	out_off = 0

	while True:
		if in_off == len(data):
			break

		cw = struct.unpack_from(">H", data, in_off)[0]
		in_off += 2

		for z in range(16):
			if in_off == len(data):
				break

			if cw & 0x8000:								# 1 = copy bytes from further back in output
				cw1 = struct.unpack_from(">H", data, in_off)[0]
				count = ((cw1 & 0xf800) >> 10) + 4					# (top 5 bits * 2) + 4 = number of bytes to copy
				back_offset = ((cw1 & 0x7ff) * 2) + 2					# back reference in output data

				for a in range(count):
					new_image[out_off + a] = new_image[out_off - back_offset + a]

				in_off += 2
				out_off += count

			else:									# 0 = copy 2 bytes from input
				new_image[out_off] = data[in_off + 1]
				new_image[out_off + 1] = data[in_off]

				in_off += 2
				out_off += 2

			cw <<=1									# next control bit

	return new_image



# Add an image segment to an image buffer with the correct palette
# new_image = buffer (existing or blank, 2048 x 2048 RGBA), source_image = decompressed main image
# source image = 2048 x 2048 (8-bit)
# source palette is ARGB

def create_segment(new_image, source_image, pal, x_off, y_off, width, height):
	for h in range(height):
		row_pos = (h + y_off) * 8192
		for w in range(width):
			w_pos = (x_off + w) * 4
			val = source_image[((h + y_off) * 2048) + x_off + w]
			new_image[row_pos + w_pos + 3] = pal[val*4]					# Alpha
			new_image[row_pos + w_pos + 0] = pal[val*4 + 1]				# Red
			new_image[row_pos + w_pos + 1] = pal[val*4 + 2]				# Green
			new_image[row_pos + w_pos + 2] = pal[val*4 + 3]				# Blue

	return new_image


# --------------------------------------------------------------------------------
# Create PNG file
# --------------------------------------------------------------------------------

# Source image should be RGBA

def make_png(img):
	width = 2048
	height = 2048
	rgba = bytearray((width * height * 4) + height)							# PNG pixel buffer

	for h in range(height):
		rgba[(h * 8193) + 1: (h * 8193) + 8193] = img[h * 8192: h * 8192 + 8192]

	comp = zlib.compress(rgba)									# Compress RGBA data for PNG

	png_header = struct.pack("8B", *b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a")
	png_ihdr = struct.pack(">4sIIBBBBB", b"IHDR", width, height, 8, 6, 0, 0, 0)
	crc_ihdr = png_crc(png_ihdr)
	crc_dat = png_crc(b"IDAT" + comp)
	crc_end = png_crc(b"IEND")

	png_file = png_header + struct.pack(">I", 0x0d) + png_ihdr + struct.pack(">I", crc_ihdr)
	png_file += struct.pack(">I", len(comp)) + b"IDAT" + comp + struct.pack(">I", crc_dat)
	png_file += struct.pack(">I", 0) + b"IEND" + struct.pack(">I", crc_end)

	return png_file


def png_crc(data):
	crc_table = []

	for n in range(256):
		c = n

		for k in range(8):
			if c & 1:
				c= 0xedb88320 ^ (c >> 1)
			else:
				c >>= 1

		crc_table.append(c)

	c = 0xffffffff

	for n in range(len(data)):
		c = crc_table[(c ^ data[n]) & 0xff] ^ (c >> 8)

	return c ^ 0xffffffff




# --------------------------------------------------------------------------------
# Main program
# --------------------------------------------------------------------------------

print("================================================================================")
print("Nitroplus Blasterz: Heroines Infinite Duel (PS3)")
print("Extract images from ITD/PIL archives")
print("Python script by DKDave, 2025")
print("================================================================================\n")

if len(sys.argv) < 2:
	print("Error:\tNo archive name provided.\n")
	print("Usage:\tPython nb_dec.py [PIL archive]")
	exit()

in_file = sys.argv[1]											# Input archive

if not os.path.exists(in_file):
	print("Error:\tFilename doesn't exist.  Please try another file.")
	exit()

f = open(in_file, "rb")

itd_file = in_file.replace(".pil", ".itd")
basename = in_file.replace(".pil", "")

if not os.path.exists(itd_file):
	print("Error:\tITD file doesn't exist.")
	f.close()
	exit()

pal = bytearray(0x400)

p = open(itd_file, "rb")
itd_data = p.read()
p.close()

codec_names = {0x29: "8-bit + palette", 0x31545844: "DXT1", 0x35545844: "DXT5"}
raw_images = []											# array of all image data

f.seek(0x0c)
files = int.from_bytes(f.read(4), "big")									# Number of images


print("Decompressing images\n")

entry = 0x10

file_types = []

for a in range(files):
	f.seek(entry + (a * 0x24))
	unk1 = int.from_bytes(f.read(4), "big")
	width = int.from_bytes(f.read(2), "big")
	height = int.from_bytes(f.read(2), "big")
	f.seek(entry + (a * 0x24) + 0x14)
	codec = int.from_bytes(f.read(4), "big")
	unk2 = int.from_bytes(f.read(4), "big")
	offset = int.from_bytes(f.read(4), "big")								# "SAP" file header
	comp_size = int.from_bytes(f.read(4), "big")

	file_types.append(codec)

	f.seek(offset + 8)
	dec_size1 = int.from_bytes(f.read(4), "big")
	dec_size2 = int.from_bytes(f.read(4), "big")
	f.seek(offset + 0x14)
	part2_offset = int.from_bytes(f.read(4), "big")

	if part2_offset == 0:										# only 1 compressed part
		comp_data = f.read(comp_size - 0x18)
		dec_data = dec(comp_data, dec_size1)
		part2_size = 0
	else:
		comp_data = f.read(part2_offset - 0x18)						# compressed part 1
		dec_data2 = dec(comp_data, dec_size1)
		part2_size = comp_size - part2_offset
		f.seek(offset + part2_offset)
		comp_data = f.read(part2_size)							# compressed part 2
		dec_data2 += dec(comp_data, dec_size2)

# Need to rearrange data if there are 2 compressed parts for DXT files (for some unknown reason ...)

		dec_data = bytearray(len(dec_data2))
		half_off = len(dec_data) // 2

		if codec == 0x31545844:
			for x in range(len(dec_data2) // 8):
				dec_data[x * 8: x * 8 + 4] = dec_data2[x * 4: (x* 4) + 4]
				dec_data[x * 8 + 4: x * 8 + 8] = dec_data2[(x * 4) + half_off: (x * 4) + half_off + 4]

		elif codec == 0x35545844:
			for x in range(len(dec_data2) // 16):
				dec_data[x * 16: x * 16 + 8] = dec_data2[x * 8: (x* 8) + 8]
				dec_data[x * 16 + 8: x * 16 + 16] = dec_data2[(x * 8) + half_off: (x * 8) + half_off + 8]

	if codec == 0x29:
		raw_images.append(dec_data)



# Reconstruct images with the correct palette for each segment
# Image segments are still "out of order" (for now)

itd_pal_off = struct.unpack_from(">I", itd_data, 0x10)[0] + 8
itd_sec1_off = struct.unpack_from(">I", itd_data, 0x14)[0]
itd_sec2_off = struct.unpack_from(">I", itd_data, 0x18)[0]

sec1_count = struct.unpack_from(">I", itd_data, itd_sec1_off + 4)[0]
sec2_count = struct.unpack_from(">I", itd_data, itd_sec2_off + 4)[0]
sec1_size = (itd_sec2_off - itd_sec1_off - 8 ) // sec1_count

print("Reconstructing images ...\n")

for a in range(files):
	itd_sec1_off = struct.unpack_from(">I", itd_data, 0x14)[0] + 8

	buffer = bytearray(2048 * 2048 * 4)							# new buffer for each file

	for b in range(sec1_count):								# Read each segment
		codec = struct.unpack_from(">i", itd_data, itd_sec1_off)[0]
		main_idx = struct.unpack_from(">i", itd_data, itd_sec1_off + 4)[0]
		pal_idx = struct.unpack_from(">i", itd_data, itd_sec1_off + 8)[0]
		x_off = struct.unpack_from(">I", itd_data, itd_sec1_off + 12)[0]
		y_off = struct.unpack_from(">I", itd_data, itd_sec1_off + 16)[0]
		width = struct.unpack_from(">I", itd_data, itd_sec1_off + 20)[0]
		height = struct.unpack_from(">I", itd_data, itd_sec1_off + 24)[0]

		if codec == 0x29 and main_idx == a:
			pal = itd_data[itd_pal_off + (pal_idx * 0x400): itd_pal_off + (pal_idx * 0x400) + 0x400]

			buffer = create_segment(buffer, raw_images[a], pal, x_off, y_off, width, height)

			final_img = make_png(buffer)

		itd_sec1_off += sec1_size

	if file_types[a] == 0x29:
		print("Writing image ... " + str(a))

		x = open(basename + "_" + str(a) + ".png", "wb")
		x.write(final_img)
		x.close()

f.close()


