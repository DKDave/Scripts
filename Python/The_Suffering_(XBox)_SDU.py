# ================================================================================
# The Suffering (XBox)
# .sdu audio extract
# Python script by DKDave, 2026
# ================================================================================

# Usage: Python sdu.py [sdu archive] [output folder]


import os, sys, struct


print("=" * 80)
print("The Suffering (XBox) - sdu audio extractor")
print("Python script by DKDave, 2026")
print("=" * 80 + "\n")

if len(sys.argv) != 3:
	print("Invalid number of parameters.  Please provide an input sdu archive and an output folder.")
	exit()

in_file = sys.argv[1]
basename = in_file.replace(".sdu", "")
out_folder = sys.argv[2]

os.makedirs(out_folder, 0o777, True)							# Create output folder in current folder

f = open(in_file, "rb")

f.seek(0)
data = f.read()
f.close()

check = struct.unpack_from("<I", data, 0)[0]

if check != 0x43535253:								# "SRSC"
	print("Not a valid SRSC file.")
	exit()

entry, files = struct.unpack_from("<II", data, 6)

print("-" * 80)
print(f"{'#':<10}{'Rate':<15}{'Chans':<10}{'Size':<15}{'Filename':<30}")
print("-" * 80 + "\n")

for a in range(files):
	type, fnum, unk1, offset, size = struct.unpack_from("<HHHII", data, entry + (a * 14))

	if type == 0x302:								# audio header (always 0x3c bytes)
		channels = struct.unpack_from("<H", data, offset + 0x2c)[0]
		rate = struct.unpack_from("<I", data, offset + 0x30)[0]
		byte_rate = (rate * channels * 4) // 32

	if type == 0x304:								# audio data (XBox ADPCM)
		audio_data = data[offset: offset + size]

		wav_header = struct.pack("<4sI8sIHHIIHHHH4sI", b"RIFF", size + 0x30, b"WAVEfmt ", 0x14, 0x69, channels, rate, byte_rate, channels * 0x24, 4, 2, 0x40, b"data", size)

		filename = out_folder + "\\" + basename + "_" + str(fnum) + ".wav"

		x = open(filename, "wb")
		x.write(wav_header)
		x.write(audio_data)
		x.close()

		print(f"{str(fnum):<10}{rate:<15}{channels:<10}{str(hex(size)):<15}{filename:<30}")

