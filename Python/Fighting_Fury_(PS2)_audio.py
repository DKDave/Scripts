# ================================================================================
# Fighting Fury (PS2)
# MUSIC.STR and VOICE.STR extract
# Python script by DKDave, 2023
# ================================================================================

# Files are extracted as .ss2 files which can be played in Foobar/vgmstream
# Put SLES_510.56, MUSIC.STR and VOICE.STR in the same folder


import sys, os, struct


print("================================================================================")
print("Fighting Fury (PS2) MUSIC.STR and VOICE.STR extractor")
print("Python script by DKDave, 2023")
print("================================================================================")
print("")

file1 = open("SLES_510.56", "rb")
file2 = open("MUSIC.STR", "rb")
file3 = open("VOICE.STR", "rb")


# MUSIC.STR

file1.seek(0xc8d60)
table = bytearray(file1.read(0x64))

for a in range(24):
	temp1 = struct.unpack_from("<II", table, a * 4)
	offset = temp1[0] * 0x800
	offset2 = temp1[1] * 0x800
	size = offset2 - offset
	interleave = size // 2

	header = struct.pack("<4sIIIIIII4sI", b"SShd", 0x18, 2, 48000, 2, interleave, 0xFFFFFFFF, 0xFFFFFFFF, b"SSbd", size)

	filename = "FF_MUSIC_" + str(a) + ".ss2"

	file2.seek(offset)
	audio_data = bytearray(file2.read(size))

	print("Writing file ... ", filename)

	outfile = open(filename, "wb")
	outfile.write(header)
	outfile.write(audio_data)
	outfile.close()


# VOICE.STR

file1.seek(0xc8dd0)
table = bytearray(file1.read(0x2d0))

for a in range(179):
	temp1 = struct.unpack_from("<II", table, a * 4)
	offset = temp1[0] * 0x800
	offset2 = temp1[1] * 0x800
	size = offset2 - offset

	header = struct.pack("<4sIIIIIII4sI", b"SShd", 0x18, 2, 24000, 1, 0, 0xFFFFFFFF, 0xFFFFFFFF, b"SSbd", size)

	filename = "FF_VOICE_" + str(a) + ".ss2"

	file3.seek(offset)
	audio_data = bytearray(file3.read(size))

	print("Writing file ... ", filename)

	outfile = open(filename, "wb")
	outfile.write(header)
	outfile.write(audio_data)
	outfile.close()


file1.close()
file2.close()
file3.close()





