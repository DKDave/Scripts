# ================================================================================
# Geist (GameCube)
# Extract audio from cutscene files
# Python script by DKDave, 2025
# ================================================================================

# Note: cutscene audio is in the ".SDF_GC" files
# Cutscene audio is stereo - files are extracted as separate DSP files for left and right audio channels, which will play as stereo in Foobar/vgmstream


import os, sys, struct


print("================================================================================")
print("Geist (GameCube)")
print("Cutscene audio extractor")
print("Python script by DKDave, 2025")
print("================================================================================\n")

if len(sys.argv) != 2:
	print("Error - File not provided\n")
	print("Usage: Python " + sys.argv[0] + " [filename]")
	exit()

filename = sys.argv[1]
basename = filename.split(".")[0]

f = open(filename, "rb")
file_size = os.path.getsize(filename)
blocks = file_size // 0x800

file_list = []

for a in range(blocks):
	f.seek(a * 0x800)
	block_type = int.from_bytes(f.read(4), "big")

	if block_type == 0x41:							# Audio block
		f.seek((a * 0x800) + 0x40)
		misc1 = int.from_bytes(f.read(4), "big")

		if misc1 == 0x7d00 or misc1 == 0xac44:					# 32000 or 44100 KHz
			file_list.append(a * 0x800)

files = len(file_list) // 2

for a in range(files):
	offset = file_list[a * 2]

	if a == files-1:
		block_end = file_size
	else:
		block_end = file_list[a * 2 + 2]

	file_blocks = (block_end - offset) // 0x800
	chan = 0
	left = bytes()
	right = bytes()

	for b in range(file_blocks):							# Process each file
		block_offset = offset + b * 0x800
		f.seek(block_offset)
		block_type = int.from_bytes(f.read(4), "big")

		if block_type == 0x41:						# Audio blocks only
			f.seek(block_offset + 0x40)
			block_data = f.read(0x7c0)					# 0x40 bytes of header in each block

			if chan == 0:						# Blocks are interleaved between left and right channels
				left += block_data
			else:
				right += block_data

			chan = 1 - chan

# left + right arrays should now contain the left and right channel audio data, so now write the files

	rate = struct.unpack_from(">I", left, 0)[0]
	coeffs_l = left[4:36]
	coeffs_r = right[4:36]
	samp_count = ((len(left) - 0x40) // 8) * 14
	nib_count = (len(left) - 0x40) * 2

	dsp_header_l = bytearray(0x60)
	struct.pack_into(">III", dsp_header_l, 0, samp_count, nib_count, rate)
	struct.pack_into(">32B", dsp_header_l, 0x1c, *coeffs_l)

	dsp_header_r = bytearray(0x60)
	struct.pack_into(">III", dsp_header_r, 0, samp_count, nib_count, rate)
	struct.pack_into(">32B", dsp_header_r, 0x1c, *coeffs_r)

	print(f"{'Writing ...':<20}{basename + '_' + str(a):<30}")

	o = open(basename + "_" + str(a) + "_l.dsp", "wb")
	o.write(dsp_header_l + left[0x40:])
	o.close()

	o = open(basename + "_" + str(a) + "_r.dsp", "wb")
	o.write(dsp_header_r + right[0x40:])
	o.close()

f.close()


