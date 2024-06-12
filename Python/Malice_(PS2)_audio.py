# ================================================================================
# Malice (PS2)
# Extract audio from various archives
# Python script by DKDave, 2024 (version 2)
# ================================================================================

# Info:
# Use this script only on the various archives that contain audio info, such as "3", "6", "e", "t1"
# The relevant "s" audio files will be detected as required


import os, sys, struct


# LZSS decompression

def dec_lzss(buffer, zsize, size):
	dec = bytearray(size)								# Decompressed buffer
	dict = bytearray(4096)

	in_off = 0
	out_off = 0
	dic_off = 0xfee
	mask = 0

	while out_off < size:
		if mask == 0:
			cb = buffer[in_off]							# Read control byte
			in_off += 1
			mask = 1								# Start from bit 0 again

		if (mask & cb):								# Copy 1 byte from source & add to dictionary
			dec[out_off] = buffer[in_off]
			dict[dic_off] = buffer[in_off]

			out_off += 1
			in_off += 1
			dic_off = (dic_off + 1) & 0xfff
		else:									# Copy data from dictionary
			b1 = buffer[in_off]
			b2 = buffer[in_off + 1]
			len = (b2 & 0x0f) + 3
			loc = b1| ((b2 & 0xf0) << 4)						# Location in dictionary

			for b in range(len):
				byte = dict[(loc+b) & 0xfff]
				dec[out_off+b] = byte
				dict[(dic_off + b) & 0xfff] = byte

			dic_off = (dic_off + len) & 0xfff

			in_off += 2
			out_off += len

		mask = (mask << 1) & 0xff

	return dec



def read_audio_info(data, offset):
	riff_type = struct.unpack_from("<4s", data, offset + 8)[0].decode("ascii")			# CVG1/WAVS/WAVE
	offset1 = offset + 12

	while True:
		block_type = struct.unpack_from("<4s", data, offset1)[0].decode("ascii")
		block_size = struct.unpack_from("<I", data, offset1 + 4)[0]

		if block_type == "name":
			filename = struct.unpack_from("<%ds" % block_size, data, offset1 + 8)[0].decode("ascii").replace("\x00", "")
			filename = filename.replace(".wav", ".ss2")
			filename = filename.replace("p:\\", "")
			filename = filename.replace("t:\\", "")
			filename = filename.replace("\\\\", "")

		if block_type == "fmt ":
			rate = struct.unpack_from("<H", data, offset1 + 0x14)[0]
			rate = (rate * 48000) // 4096
			channels = struct.unpack_from("<H", data, offset1 + 0x1a)[0]
			channels = (channels & 1) + 1

			if channels == 1:
				interleave = 0
			else:
				interleave = 0x400

		if block_type == "data":
			audio_size = block_size
			data_offset = offset1 + 8
			break

		if block_type == "strm":
			audio_size = struct.unpack_from("<I", data, offset1 + 0x0c)[0]
			data_offset = -1
			break

		offset1 += block_size + 8

	return [riff_type, filename, rate, channels, interleave, audio_size, data_offset]


# Main program

in_file = sys.argv[1]

f = open(in_file, "rb")

if in_file[0] == "s":
	print("Not an archive")
	f.close()
	exit()

if in_file[0] == "t":
	audio_file = in_file.replace("t", "s")
else:
	audio_file = "s"

if os.path.exists(audio_file):
	f2 = open(audio_file, "rb")
	f2_exists = 1
else:
	print("External audio file not loaded.")
	f2_exists = 0

f.seek(0x64)
count1 = int.from_bytes(f.read(4), "little")
count2 = int.from_bytes(f.read(4), "little")

table = 0x70 + (count2 * 8)
offset = 0x800

for a in range(count1):
	f.seek(table + (a * 12))
	type = int.from_bytes(f.read(2), "little")								# 0x1700 = audio
	total_blocks = int.from_bytes(f.read(2), "little")
	zsize = int.from_bytes(f.read(4), "little")
	size = int.from_bytes(f.read(4), "little")

	if type == 0x1700:										# Audio info

		if zsize != size:									# Decompress data if required
			f.seek(offset + 8)
			comp_data = f.read(zsize)
			data = bytearray(8) + dec_lzss(comp_data, zsize, size)
		else:
			f.seek(offset)
			data = f.read(zsize+8)

		files = struct.unpack_from("<I", data, 8)[0]
		entry = 0x0c									# Start of file info + data

		for b in range(files):
			total_size = struct.unpack_from("<I", data, entry)[0]
			entry_type = struct.unpack_from("<I", data, entry + 4)[0]				# 1 = audio data follows in this file, 5 = audio data in external file

			if entry_type == 1:								# internal audio
				info = read_audio_info(data, entry + 12)

				ss2_header = struct.pack("<4sIIIIIII4sI", b"SShd", 0x18, 2, info[2], info[3], 0, 0xFFFFFFFF, 0xFFFFFFFF, b"SSbd", info[5])
				audio_data = data[info[6]:info[6] + info[5]]

			elif entry_type == 5:								# external audio
				audio_offset = struct.unpack_from("<I", data, entry + 0x0c)[0]
				audio_size = struct.unpack_from("<I", data, entry + 0x10)[0]
				info = read_audio_info(data, entry + 0x14)

				ss2_header = struct.pack("<4sIIIIIII4sI", b"SShd", 0x18, 2, info[2], info[3], info[4], 0xFFFFFFFF, 0xFFFFFFFF, b"SSbd", info[5])
				f2.seek(audio_offset)
				audio_data = f2.read(info[5])

			if entry_type == 1 or entry_type == 5:
				folder = os.path.dirname(info[1])
				os.makedirs(folder, 0o777, True)
				filename = os.path.basename(info[1])

				if os.path.exists(folder + "\\" + filename):
					print(folder + "\\" + filename + " already exists")
				else:
					f3 = open(folder + "\\" + filename, "wb")
					f3.write(ss2_header)
					f3.write(audio_data)
					f3.close()

					print(f"{b:<10}{info[0]:<10}{info[2]:<10}{info[3]:<10}{info[5]:<12}{info[1]}")

			entry += total_size + 4

	offset += (total_blocks * 0x800)

if f2_exists == 1:
	f2.close()

f.close()


