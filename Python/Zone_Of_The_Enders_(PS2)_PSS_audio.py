# ================================================================================
# Zone Of The Enders (PS2)
# Extract audio from PSS files
# Python script by DKDave, 2024
# ================================================================================

# This script will process all PSS files in the current folder and output playable .ss2 files
# Usage:	Python zoe.py [output folder]

# Note: These are not the usual PSS video files found in other games


import os, sys, struct, glob


def read_file(filename, out_folder):
	basename = filename.split(".")[0]
	out_name = basename + ".ss2"
	os.makedirs(out_folder, 0o777, True)

	chan_text = {1: "Mono", 2: "Stereo"}
	audio = bytearray()
	offset = 0

	f = open(filename, "rb")

	while True:
		f.seek(offset)
		chunk_type = int.from_bytes(f.read(4), "big")

		if chunk_type == 0x1b9:						# End of file
			break

		if chunk_type == 0x1ba:						# File header
			chunk_size = 8
		else:
			chunk_size = int.from_bytes(f.read(2), "big")

		if chunk_type == 0x1bd:						# Data chunk
			f.seek(offset + 22)
			data_type = int.from_bytes(f.read(1), "big")

			if data_type == 1:						# Audio
				audio += f.read(chunk_size - 17)

		offset += chunk_size + 6

	if len(audio) == 0:
		print("No audio in " + filename)
		return

	size = len(audio) - 0x800
	rate, channels = struct.unpack_from(">HB", audio, 6)
	ss2_header = struct.pack("<4sIIIIIII4sI", b"SShd", 0x18, 2, rate, channels, 0x800, 0xFFFFFFFF, 0xFFFFFFFF, b"SSbd", size)

	print(f"{'Writing  ... ' + out_name:<35}{str(rate) + ' Hz':<15}{chan_text[channels]:<15}{str(size) + ' bytes':<20}")

	for a in range(size // 0x10):							# Remove annoying end click
		temp = struct.unpack_from("<14s", audio, 0x800 + (a * 0x10) + 2)[0]

		if temp == b"wwwwwwwwwwwwww":
			struct.pack_into("<B", audio, 0x800 + (a * 0x10) + 1, 7)

	out = open(out_folder + "\\" + out_name, "wb")
	out.write(ss2_header + audio[0x800:])
	out.close()

	f.close()


	return


print("================================================================================")
print("Zone Of The Enders (PS2) - PSS audio extract")
print("Python script by DKDave, 2024")
print("================================================================================\n")

if len(sys.argv) != 2:
	print("Usage: Python zoe.py [output folder]")
	exit()

for filename in glob.glob("*.pss"):
	read_file(filename, sys.argv[1])

