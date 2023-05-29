# ================================================================================
# Moorhuhn X (aka Crazy Chicken) (PC)
# Decompress sprite data in .rle files
# Noesis script by DKDave, 2023
# ================================================================================


from inc_noesis import *

def registerNoesisTypes():
	handle = noesis.register("Moorhuhn X: Crazy Chicken (PC)",".rle")
	noesis.setHandlerTypeCheck(handle, bcCheckType)
	noesis.setHandlerLoadModel(handle, bcLoadModel)
	return 1


# Check file type

def bcCheckType(data):
	return 1


# Read the model data

def bcLoadModel(data, mdlList):
	bs = NoeBitStream(data)

	curr_file = rapi.getLocalFileName(rapi.getInputName()).lower()
	basename = curr_file.replace(".rle", "")

	tex_list = []

	bs.seek(0x0c)
	pal = bs.readBytes(0x400)
	bs.seek(0x814)
	bit_depth = bs.readUInt()							# Always 8-bit in this game ?
	bs.seek(0x81c)
	image_count = bs.readUInt()

	offset = 0x820								# start of first image header

	for a in range(image_count):
		bs.seek(offset)
		width = bs.readUInt()
		height = bs.readUInt()
		bs.seek(offset + 0x18)
		comp_size = bs.readUInt()
		bs.seek(offset + 0x20)

		comp_data = bs.readBytes(comp_size)
		dec_data = dec_rle(comp_data, width * height)

		final_image = rapi.imageDecodeRawPal(dec_data, pal, width, height, 8, "b8g8r8a8")
		tex1 = NoeTexture(basename + "_" + str(a), width, height, final_image, noesis.NOESISTEX_RGBA32)
		tex_list.append(tex1)

		offset += comp_size + 0x20

	mdl = NoeModel()
	mdl.setModelMaterials(NoeModelMaterials(tex_list, []))
	mdlList.append(mdl)

	return 1


# RLE decompression

def dec_rle(data, dec_size):
	out_buffer = bytearray(dec_size)
	in_off = 0
	out_off = 0

	while in_off < len(data):
		control_byte = data[in_off]
		in_off += 1

		if control_byte >= 128:						# copy bytes from input
			count = 256 - control_byte

			for a in range(count):
				out_buffer[out_off + a] = data[in_off + a]

			out_off += count
			in_off += count
		else:								# repeat a byte xx times
			count = control_byte
			repeat_byte = data[in_off]
			in_off += 1

			for a in range(count):
				out_buffer[out_off + a] = repeat_byte

			out_off += count

	return out_buffer

