# ================================================================================
# Nuclear Strike (PS1)
# FSV/WVE audio extract
# Python script by DKDave, 2023
# ================================================================================

# Files are extracted as .ss2 files which can be played in Foobar/vgmstream


import sys, os, struct


# --------------------------------------------------------------------------------
# Decode au chunk
# data = au00 or au01 chunk bytearray
# --------------------------------------------------------------------------------

def au_dec(data):
	stream = bytearray()
	size = struct.unpack_from(">I", data, 4)[0]
	parts = (size - 0x10) // 0x1e									# parts per channel

	left = 0x10											# offset of left channel audio data
	right = (parts * 0x0f) + 0x10									# offset of right channel audio data

	for a in range(parts):
		stream += data[left + (a * 0x0f): left + (a * 0x0f) + 1]
		stream += b'\x00'									# add byte for ADPCM flags
		stream += data[left + (a * 0x0f) + 1: left + (a * 0x0f) + 15]

		stream += data[right + (a * 0x0f): right + (a * 0x0f) + 1]
		stream += b'\x00'
		stream += data[right + (a * 0x0f) + 1: right + (a * 0x0f) + 15]

	return stream



print("================================================================================")
print("Nuclear Strike (PS1) - FSV/WVE audio extractor")
print("Python script by DKDave, 2023")
print("================================================================================")
print("")

if len(sys.argv) != 2:
	print("Error:\tNot enough parameters given.")
	print("\nUsage:\tpython fsv.py [FSV or WVE video file]")
	exit()

filename = sys.argv[1]
file1 = open(filename, "rb")
vid = bytearray(file1.read())
file1.close()

filename = sys.argv[1].split(".")[0]

audio_stream = bytearray()
audio_stream += struct.pack("<4sIIIIIII4sI", b"SShd", 0x18, 2, 22050, 2, 0x10, 0xFFFFFFFF, 0xFFFFFFFF, b"SSbd", 0)		# SS2 header

offset = 0

while True:
	if offset == len(vid):
		break

	chunk_type = struct.unpack_from(">4s", vid, offset)[0].decode("ascii")
	chunk_size = struct.unpack_from(">I", vid, offset + 4)[0]

	if chunk_type == "au00" or chunk_type == "au01":
		audio_stream += au_dec(vid[offset:offset + chunk_size])

	offset += chunk_size

audio_size = len(audio_stream)
struct.pack_into("<I", audio_stream, 0x24, audio_size)

out_file = open(filename + ".ss2", "wb")
out_file.write(audio_stream)
out_file.close()




