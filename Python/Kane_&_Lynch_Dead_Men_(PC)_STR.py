# ================================================================================
# Kane & Lynch: Dead Men (PC, 2007)
# STR audio extract
# Python script by DKDave, 2025
# Last updated: 2 February 2025
# ================================================================================

# Use: Python str.py [STR archive]


import os, struct, sys


# Deinterleave data
# Interleaved data, stride size, offset within stride, size of data within stride

def de_inter(temp_data, block_size, element_off, element_size):
	block_count = len(temp_data) // block_size

	new_data = bytearray(block_count * element_size)

	for x in range(block_count):
		temp = temp_data[x * block_size + element_off: x * block_size + element_off + element_size]
		new_data[x * element_size: x * element_size + len(temp)] = temp

	return new_data


print("================================================================================")
print("Kane & Lynch: Dead Men (PC)")
print("STR audio archive extractor")
print("Python script by DKDave, 2025")
print("================================================================================\n")

types = {2: "PCM16", 3: "IMA", 4: "Ogg", 26: "PCM16 (Interleaved)"}
ch = {1: "Mono", 2: "Stereo"}


if len(sys.argv) != 2:
	print("Please provide an .STR file to process.")
	exit()

f = open(sys.argv[1], "rb")

f.seek(0)
check = f.read(12)

if check != B"IOISNDSTREAM":
	print("Invalid file.")
	f.close()
	exit()

f.seek(0x18)
temp1 = int.from_bytes(f.read(4), "little")
files = int.from_bytes(f.read(4), "little")

f.seek(temp1)
table1 = f.read(files * 0x48)
list = []

for a in range(files):
	id = struct.unpack_from("<Q", table1, a * 0x48)[0]
	offset = struct.unpack_from("<Q", table1, a * 0x48 + 8)[0]
	size = struct.unpack_from("<Q", table1, a * 0x48 + 16)[0]
	metadata_off = struct.unpack_from("<Q", table1, a * 0x48 + 24)[0]
	meta_size = struct.unpack_from("<I", table1, a * 0x48 + 0x20)[0]
	entry_unk1 = struct.unpack_from("<I", table1, a * 0x48 + 0x24)[0]
	name_len = struct.unpack_from("<Q", table1, a * 0x48 + 0x28)[0]
	name_off = struct.unpack_from("<Q", table1, a * 0x48 + 0x30)[0]
	entry_unk2 = struct.unpack_from("<I", table1, a * 0x48 + 0x38)[0]
	entry_unk3 = struct.unpack_from("<I", table1, a * 0x48 + 0x3c)[0]
	entry_unk4 = struct.unpack_from("<I", table1, a * 0x48 + 0x40)[0]
	entry_unk5 = struct.unpack_from("<I", table1, a * 0x48 + 0x44)[0]

	f.seek(name_off)
	filename = f.read(name_len).decode("ascii")

	f.seek(metadata_off)
	type = int.from_bytes(f.read(4), "little")
	samps = int.from_bytes(f.read(4), "little")
	channels = int.from_bytes(f.read(4), "little")
	rate = int.from_bytes(f.read(4), "little")
	bits = int.from_bytes(f.read(4), "little")
	f.read(8)

	interleave = 0
	spb = 0

	if type == 2:
		interleave = int.from_bytes(f.read(4), "little")

	if type == 3:
		interleave = int.from_bytes(f.read(4), "little")
		spb = int.from_bytes(f.read(4), "little")

	f.seek(offset)
	lip_check = f.read(4)

	if lip_check == b"LIP ":
		offset += 0x1000

	list.append([id, offset, size, metadata_off, meta_size, entry_unk1, filename, entry_unk2, entry_unk3, entry_unk4, entry_unk5, type, samps, channels, rate, bits, interleave, spb])


list.sort()

print("------------------------------------------------------------------------------------------------------------------------------------------------------")
print(f"{'ID':<10}{'Size':<15}{'Type':<25}{'Channels':<10}{'Rate':<10}{'Filename':<100}")
print("------------------------------------------------------------------------------------------------------------------------------------------------------\n")

for a in range(files):
	info = list[a]

	id = info[0]
	offset = info[1]
	size = info[2]
	filename = info[6]
	idx = info[9]										# stream count for type 26 files
	type = info[11]
	channels = info[13]
	rate = info[14]
	bits = info[15]
	interleave = info[16]
	spb = info[17]
	folder = os.path.dirname(filename)

	if type == 4:										# Ogg
		filename = filename.replace(".wav", ".ogg")

		f.seek(offset)
		data = f.read(size)

		os.makedirs(folder, 0o777, True)
		out = open(filename, "wb")
		out.write(data)
		out.close()

	if type == 3:										# MS IMA
		print(f"{id:<10}{size:<15}{types[type]:<25}{ch[channels]:<10}{rate:<10}{filename:<100}")

		wav_header = struct.pack("<4sI8sIHHIIHHHI4sI", b"RIFF", size + 0x2a, b"WAVEfmt ", 0x16, 0x11, channels, rate, (rate * interleave) // spb, interleave, 4, 4, spb, b"data", size)
		f.seek(offset)
		data = f.read(size)

		os.makedirs(folder, 0o777, True)
		out = open(filename, "wb")
		out.write(wav_header + data)
		out.close()

	if type == 2 and idx == 0:									# PCM16
		print(f"{id:<10}{size:<15}{types[type]:<25}{ch[channels]:<10}{rate:<10}{filename:<100}")

		wav_header = struct.pack("<4sI8sIHHIIHH4sI", b"RIFF", size + 0x24, b"WAVEfmt ", 0x10, 1, channels, rate, rate * (channels // 8), channels * (bits //8), bits, b"data", size)
		f.seek(offset)
		data = f.read(size)

		os.makedirs(folder, 0o777, True)
		out = open(filename, "wb")
		out.write(wav_header + data)
		out.close()

	if type == 26:										# PCM16 (interleaved streams)
		stride = 0

		for b in range(idx):
			stream_rate = list[a+b+1][14]							# Sample rate for this stream
			multiplier = 4 * (stream_rate / rate)
			stride += multiplier

		f.seek(offset)
		int_data = f.read(size)								# Interleaved data

		inter_off = 0

		for b in range(idx):									# For each stream
			filename = list[a+b+1][6]
			folder = os.path.dirname(filename)
			stream_id = list[a+b+1][0]
			stream_size = list[a+b+1][2]
			stream_channels = list[a+b+1][13]
			stream_rate = list[a+b+1][14]
			stream_bits = list[a+b+1][15]
			stream_interleave = list[a+b+1][16]

			multiplier = 4 * (stream_rate / rate)
			data = de_inter(int_data, int(stride), int(inter_off), int(multiplier))

			inter_off += multiplier

			wav_header = struct.pack("<4sI8sIHHIIHH4sI", b"RIFF", stream_size + 0x24, b"WAVEfmt ", 0x10, 1, stream_channels, stream_rate, stream_rate * (stream_channels // 8), stream_channels * (stream_bits //8), stream_bits, b"data", stream_size)

			print(f"{stream_id:<10}{stream_size:<15}{types[type]:<25}{ch[stream_channels]:<10}{stream_rate:<10}{filename:<100}")

			os.makedirs(folder, 0o777, True)
			out = open(filename, "wb")
			out.write(wav_header + data)
			out.close()


f.close()


