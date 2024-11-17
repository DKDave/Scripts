# ================================================================================
# Star Trek: Conquest (PS2)
# PSH/PSK audio extract
# Python script by DKDave, 2024
# ================================================================================

# Tested on Python v3.9.5
# Also works for other games such as State Of Emergency 2 (PS2)
# Some games have additional .SYM files which contain filenames - these are not yet supported

# Usage: Python psh.py [PSH file] [output folder]


import os, sys, struct

print("--------------------------------------------------------------------------------")
print("Star Trek: Conquest (PS2) - PSH/PSK audio extract")
print("Python script by DKDave, 2024")
print("--------------------------------------------------------------------------------\n")

chans = ["Mono", "Stereo"]

if len(sys.argv) != 3:
	print("**\tIncorrect parameters")
	print("**\tUsage: Python " + sys.argv[0] +  " [PSH file] [output folder]")
	print("**\t(Output folder will be created if it doesn't exist)")
	exit()

psh_file = sys.argv[1]
psk_file = psh_file.replace(".psh", ".psk")
out_folder = sys.argv[2]

if os.path.exists(out_folder):
	print("**\tOutput folder " + out_folder + " already exists")
else:
	os.makedirs(out_folder, 0o777, True)
	print("**\tOutput folder " + out_folder + " created")

psh = open(psh_file, "rb")
psk = open(psk_file, "rb")
basename = psh_file.replace(".psh", "")

psh.seek(0x14)
table1 = int.from_bytes(psh.read(4), "little")								# Section info
psh.seek(0x1c)
table2 = int.from_bytes(psh.read(4), "little") + 0x48								# File info (offsets/size/rate)
sections = int.from_bytes(psh.read(4), "little")

for a in range(sections):
	psh.seek(table1 + (a * 0x38) + 4)
	info1 = int.from_bytes(psh.read(4), "little")
	psh.seek(table1 + (a * 0x38) + 0x33)
	files = int.from_bytes(psh.read(4), "little")

	for b in range(files):
		psh.seek(info1 + (b * 0x24))
		entry_type = int.from_bytes(psh.read(4), "little")

		if entry_type == 0:
			file_idx = int.from_bytes(psh.read(4), "little")
			psh.seek(table2 + (file_idx * 0x44) + 0x14)
			offset = int.from_bytes(psh.read(4), "little")
			size = int.from_bytes(psh.read(4), "little")
			rate = int.from_bytes(psh.read(4), "little")
			psh.seek(table2 + (file_idx * 0x44) + 0x28)
			interleave = int.from_bytes(psh.read(4), "little") // 4				# = 0 for mono files

			if interleave == 0:
				channels = 1
			else:
				channels = 2

# Create ss2 header

			if channels == 1:
				ss2_header = struct.pack("<4sIIIIIII4sI", b"SShd", 0x18, 2, rate, 1, 0, 0xFFFFFFFF, 0xFFFFFFFF, b"SSbd", size)
			else:
				ss2_header = struct.pack("<4sIIIIIII4sI", b"SShd", 0x18, 2, rate, 2, interleave, 0xFFFFFFFF, 0xFFFFFFFF, b"SSbd", size)

			psk.seek(offset)
			audio_data = psk.read(size)
			out_file = out_folder + "\\" + basename + "_" + str(file_idx) + ".ss2"

			if os.path.exists(out_file):
				print("**\tOutput file " + out_file + " already exists and will not be overwritten")
			else:
				print(f"{'Writing ... ' + out_file:<40}{str(rate) + ' Hz':<15}{chans[channels-1]:<15}{str(size) + ' bytes':<20}")
				out = open(out_file, "wb")
				out.write(ss2_header + audio_data)
				out.close()

		else:
			print("Unknown entry type")


psh.close()
psk.close()
