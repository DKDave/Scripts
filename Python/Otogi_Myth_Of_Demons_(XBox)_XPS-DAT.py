# ================================================================================
# Otogi: Myth Of Demons (XBox, 2002)
# XPS/DAT audio extract
# Python script by DKDave, 2024
# ================================================================================


import os, sys, struct

print("================================================================================")
print("Otogi: Myth Of Demons (XBox) - XPS/DAT audio extract")
print("Python script by DKDave, 2024")
print("================================================================================\n")


if len(sys.argv) != 2:
	print("Please provide an .XPS file")
	exit()

in_file = sys.argv[1]
dat_file = in_file.replace(".xps", ".dat")

if not os.path.exists(in_file):
	print("XPS file not found.")
	exit()

if not os.path.exists(dat_file):
	print("DAT file not found.")
	exit()


f = open(in_file, "rb")
s = open(dat_file, "rb")

f.seek(4)
files = int.from_bytes(f.read(4), "little")
entry = 0x10

sounds = {}
names = {}


# Create an array of sound and filename IDs from XPS file

for a in range(files):
	f.seek(entry)
	data_size = int.from_bytes(f.read(4), "little")
	entry_type = int.from_bytes(f.read(4), "little")
	padding_size = int.from_bytes(f.read(4), "little")
	unk1= int.from_bytes(f.read(4), "little")

	if entry_type == 0x646973:							# "sid"
		sound_id = int.from_bytes(f.read(4), "little")
		name_id = int.from_bytes(f.read(4), "little")

		sounds[sound_id] = name_id

	if entry_type == 0x73736475:							# "udss"
		name_id = int.from_bytes(f.read(4), "little")
		unk1 = int.from_bytes(f.read(4), "little")
		filename = f.read(data_size - 8)
		filename = filename.decode("ascii").replace("\x00", "").replace("d:\\", "")

		names[name_id] = filename

	entry += data_size + padding_size + 0x10


# Process DAT file

s.seek(4)
dat_files = int.from_bytes(s.read(4), "little")
entry = 0x20

for a in range(dat_files):
	s.seek(entry)
	sound_id = int.from_bytes(s.read(4), "little")
	name_id = sounds[sound_id]
	filename = names[name_id]
	offset = int.from_bytes(s.read(4), "little")
	size = int.from_bytes(s.read(4), "little")
	s.seek(entry + 0x18)
	wav_info = s.read(0x10)
	s.seek(offset)
	data = s.read(size)

	wav_header = struct.pack("<4sI8sI", b"RIFF", size + 0x24, b"WAVEfmt ", 0x10) + wav_info + struct.pack("<4sI", b"data", size)

	folder = os.path.dirname(filename)
	os.makedirs(folder, 0o777, True)

	if not os.path.exists(filename):
		print("Writing file ... " + filename)
		out = open(filename, "wb")
		out.write(wav_header + data)
		out.close()
	else:
		print("File already exists ... " + filename)

	entry += 0x94


f.close()
s.close()



