# Fragments Blue (PS2)
# View images in .obj files
# Noesis script by DKDave, 2024


from inc_noesis import *


def registerNoesisTypes():
	handle = noesis.register("Fragments Blue (PS2) - Images",".obj")
	noesis.setHandlerTypeCheck(handle, bcCheckType)
	noesis.setHandlerLoadModel(handle, bcLoadModel)
	return 1


# Check file type

def bcCheckType(data):
	return 1


# Read the model data

def bcLoadModel(data, mdlList):
	bs = NoeBitStream(data)
	ctx = rapi.rpgCreateContext()

	curr_file = rapi.getLocalFileName(rapi.getInputName()).lower().replace(".obj", "")

	tex_list = []

	pal = bs.readBytes(0x400)
	raw_image = bytearray()

	width = 640
	height = 448

	offset = 0x800
	bs.seek(offset)
	parts = bs.readUInt()

# First decompress and combine the parts that make up the image

	for a in range(parts):
		bs.seek(offset + 4 + (a * 4))
		part_offset = bs.readUInt()
		part_size = bs.readUInt() - part_offset
		part_offset += offset

		bs.seek(part_offset)
		size = bs.readUInt()
		comp_data = bs.readBytes(part_size - 4)

		raw_image += dec_lzss(comp_data, part_size - 4, size)

	final_image = rapi.imageDecodeRawPal(raw_image, pal, width, height, 8, "r8g8b8a8", noesis.DECODEFLAG_PS2SHIFT)

	tex1 = NoeTexture(curr_file, width, height, final_image, noesis.NOESISTEX_RGBA32)
	tex_list.append(tex1)

	mdl = NoeModel()
	mdl.setModelMaterials(NoeModelMaterials(tex_list, []))
	mdlList.append(mdl)

	return 1


# PS2 palette swizzle
# not needed for Noesis

def ps2_pal(pal):
	new_pal = bytearray(0x400)

	for a in range(0, 0x400, 0x80):
		new_pal[a:a + 0x20] = pal[a: a + 0x20]
		new_pal[a + 0x20: a + 0x40] = pal[a + 0x40: a + 0x60]
		new_pal[a + 0x40: a + 0x60] = pal[a + 0x20: a + 0x40]
		new_pal[a + 0x60:a + 0x80] = pal[a + 0x60: a + 0x80]

	return new_pal


# LZSS decompression

def dec_lzss(buffer, zsize, size):
	dec = bytearray(size)
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

