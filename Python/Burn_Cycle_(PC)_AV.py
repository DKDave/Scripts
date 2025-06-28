# ================================================================================
# Burn Cycle (PC)
# BURNCYC.AV audio extract
# Python script by DKDave, 2025
# ================================================================================

# Notes:
# This script extracts the audio from the video files and saves them as playable .wav files
# Ensure that BURNCYCL.AV is in the same folder as this script
# Usage: Python av.py [output folder]


import os, sys, struct


print("================================================================================")
print("Burn Cycle (PC) - .AV audio extract")
print("Python script by DKDave, 2024")
print("================================================================================\n")

# Do some checks

if len(sys.argv) != 2:
	print("Invalid command line parameter.  Please provide an output folder name.")
	exit()

out_folder = sys.argv[1]
os.makedirs(out_folder, 0o777, True)

in_file = "BURNCYCL.AV"

if os.path.exists(in_file):
	f = open(in_file, "rb")
else:
	print("BURNCYCL.AV not found.  Ensure that BURNCYCL.AV is in the same folder as this script.")
	exit()

f.seek(0)
check = int.from_bytes(f.read(4), "big")

if check != 0x4d415020:
	print("File ID invalid.  Please use a valid BURNCYCL.AV file is the same folder as this script.")
	f.close()
	exit()


# Read file table and extract audio data from each file

files = int.from_bytes(f.read(4), "big") // 4

entry = 8

for a in range(files):
	f.seek(entry + (a * 4))
	offset = int.from_bytes(f.read(4), "big")

	audio = bytes()

	while True:
		f.seek(offset)
		chunk_name = f.read(4).decode("ascii").lower()
		chunk_size = int.from_bytes(f.read(4), "big")

		if chunk_name == "eor ":
			break

		if chunk_name == "a228":					# Audio chunk
			audio += f.read(chunk_size)

		offset += chunk_size + 8

		if offset &1:						# Chunks are aligned to even-byte offsets
			offset += 1


# Write the file

	out_file = out_folder + "\\BURNCYCLAV_" + str(a) + ".wav"

	if len(audio) > 0:
		if os.path.exists(out_file):
			print(f"{a:<10}{len(audio):<20}{out_file:<30}{'File already exists':<20}")
		else:
			print(f"{a:<10}{len(audio):<20}{out_file:<30}{'Writing file'}")
			wav_header = struct.pack("<4sI8sIHHIIHH4sI", b"RIFF", len(audio) + 0x24, b"WAVEfmt ", 0x10, 1, 1, 22050, 22050, 1, 8, b"data", len(audio))	
			o = open(out_file, "wb")
			o.write(wav_header)
			o.write(audio)
			o.close()

f.close()

