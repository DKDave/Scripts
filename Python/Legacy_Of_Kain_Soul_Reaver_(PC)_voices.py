# ================================================================================
# Legacy Of Kain: Soul Reaver (PC)
# voices.dat audio extract
# Python script by DKDave, 2025
# ================================================================================

# Required files: voices.dat and kain2.exe
# Usage: Python lok.py [output folder]


import os, sys, struct


print("================================================================================")
print("Legacy Of Kain: Soul Reaver (PC) - voices.dat extract")
print("Python script by DKDave, 2025")
print("================================================================================\n")

voice_file = "voices.dat"
exe_file = "kain2.exe"

if not os.path.exists(voice_file):
	print("Voices.dat file not found.")
	exit()

if not os.path.exists(exe_file):
	print("kain2.exe file not found.")
	exit()

if len(sys.argv) != 2:
	print("Please provide an output folder name.")
	exit()

out_folder = sys.argv[1]
os.makedirs(out_folder, 0o777, True)

vd = open(voice_file, "rb")
exe = open(exe_file, "rb")

exe.seek(0xfc210)

for a in range(479):
	offset = int.from_bytes(exe.read(4), "little")
	size = int.from_bytes(exe.read(4), "little")

	vd.seek(offset)
	audio = vd.read(size)

	wav_header = struct.pack("<4sI8sIHHIIHH4sI", b"RIFF", len(audio) + 0x24, b"WAVEfmt ", 0x10, 1, 1, 22050, 44100, 2, 16, b"data", len(audio))	

	out_file = out_folder + "\loksr_voice_" + str(a) + ".wav"

	if os.path.exists(out_file):
		print(f"{out_file:<30}{hex(offset):<20}{hex(size):<20}{'File already exists - not overwritten':30}")
	else:
		print(f"{out_file:<30}{hex(offset):<20}{hex(size):<20}")

		o = open(out_file, "wb")
		o.write(wav_header)
		o.write(audio)
		o.close()


exe.close()
vd.close()


