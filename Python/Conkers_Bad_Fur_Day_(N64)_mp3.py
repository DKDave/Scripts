# ================================================================================
# Conker's Bad Fur Day (N64)
# Extract and fix mp3 files from n64 rom
# Python script by DKDave, 2025
# ================================================================================


import os, sys, struct

v1_l1_rates = [-1, 32, 64, 96, 128, 160, 192, 224, 256, 288, 320, 352, 384, 416, 448, -1]
v1_l2_rates = [-1, 32, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 384, -1]
v1_l3_rates = [-1, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, -1]
v2_l1_rates = [-1, 32, 48, 56, 64, 80, 96, 112, 128, 144, 160, 176, 192, 224, 256, -1]
v2_l2_rates = [-1, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160, -1]

m1_rates = [44100, 48000, 32000, -1]
m2_rates = [22050, 24000, 16000, -1]
m25_rates = [11025, 12000, 8000, -1]


print("--------------------------------------------------------------------------------")
print("Conker's Bad Fur Day (N64) - MP3 extractor")
print("Python script by DKDave, 2025")
print("--------------------------------------------------------------------------------\n")

if len(sys.argv) != 3:
	print("Invalid parameters.  Please provide a rom file name and an output folder.")
	exit()

rom_file = sys.argv[1]
out_folder = sys.argv[2]

os.makedirs(out_folder, 0o777, True)

f = open(rom_file, "rb")
f.seek(0x1330478)										# Audio table

data = f.read(0x167e570)									# Total size of audio data
new = bytearray(len(data))
f.close()


# Swap bytes so that data is in the correct format

for a in range(len(data) // 2):
	temp = struct.unpack_from(">H", data, a * 2)[0]
	struct.pack_into("<H", new, a * 2, temp)


# Process files

for a in range(462):
	offset = struct.unpack_from(">I", new, a * 8)[0]
	size = struct.unpack_from(">I", new, (a * 8) + 4)[0] & 0x7fffffff

	audio_data = new[offset: offset + size]

# Extract mp3 frames from the file

	frame_offset = 0
	new_audio = bytes()

	while True:
		frame_offset = audio_data.find(b"\xff\xf3", frame_offset)				# Find next MP3 frame

		if frame_offset == -1:							# No more frames found in this file
			break

		frame_header = struct.unpack_from(">I", audio_data, frame_offset)[0]
		sync = (frame_header & 0xffe00000) >> 21
		mpid = (frame_header & 0x180000) >> 19
		layer_type = (frame_header & 0x60000) >> 17
		prot = (frame_header & 0x10000) >> 16
		br_idx = (frame_header & 0xf000) >> 12
		sr_idx = (frame_header & 0xc00) >> 10
		pad = (frame_header & 0x200) >> 9
		ch_mode = (frame_header & 0xc0) >> 6

# Calculate frame size from header info

		if pad == 1:
			if layer_type == 3:							# Layer 1
				pad_size = 4
			else:
				pad_size = 1						# Layer 2 & 3
		else:
			pad_size = 0

		if mpid == 3 and layer_type == 3:						# V1 L1
			bitrate = v1_l1_rates[br_idx]
		elif mpid == 3 and layer_type == 2:						# V1 L2
			bitrate = v1_l2_rates[br_idx]
		elif mpid == 3 and layer_type == 1:						# V1 L3
			bitrate = v1_l3_rates[br_idx]
		elif mpid == 2 and layer_type == 3:						# V2 L1
			bitrate = v2_l1_rates[br_idx]
		elif mpid == 2 and (layer_type == 2 or layer_type == 1):				# V2, L2 & L3
			bitrate = v2_l2_rates[br_idx]
		else:
			bitrate = -1

		bitrate *= 1000

		if mpid == 3:								# V1
			samp_rate = m1_rates[sr_idx]
		elif mpid == 2:								# V2
			samp_rate = m2_rates[sr_idx]

		if ch_mode == 3:
			channels = 1
		else:
			channels = 2

		frame_size = ((bitrate * channels * 72) // samp_rate) + pad_size

		if samp_rate != -1:
			new_audio += audio_data[frame_offset: frame_offset + frame_size]

		if frame_size < 0:
			break

		frame_offset += frame_size

	if len(new_audio) > 0:
		print(f"{'Writing file ' + str(a):<30}{hex(offset):<20}{str(len(new_audio)) + ' bytes':<30}")
		x = open(out_folder  + "\\conker_" + str(a) + ".mp3", "wb")
		x.write(new_audio)
		x.close()


