# Forspoken (PC)
# BTEX Texture viewer
# Noesis script by DKDave, 2023


from inc_noesis import *

def registerNoesisTypes():
	handle = noesis.register("Forspoken (PC)",".btex")
	noesis.setHandlerTypeCheck(handle, CheckType)
	noesis.setHandlerLoadRGBA(handle, LoadRGBA)
	return 1


# Check file type

def CheckType(data):
	bs = NoeBitStream(data)

	id = bs.readUInt()

	if id != 0x58455442:								# "BTEX"
		return 0
	else:
		return 1


def LoadRGBA(data, texList):
	bs = NoeBitStream(data)
	curr_file = rapi.getLocalFileName(rapi.getInputName()).lower()
	tex_name = curr_file.replace(".btex", "")

	bs.seek(4)
	data_offset = bs.readUInt()
	data_size = bs.readUInt()
	bs.seek(0x20)
	width = bs.readUShort()
	height = bs.readUShort()
	bs.readUShort()
	tex_type = bs.readUShort()

	bs.seek(data_offset)
	raw_image = bs.readBytes(data_size)

	if tex_type == 0x18:
		fmt = noesis.FOURCC_BC1
	elif tex_type == 0x1a:
		fmt = noesis.FOURCC_BC3
	elif tex_type == 0x21:
		fmt = noesis.FOURCC_BC4
	elif tex_type == 0x22:
		fmt = noesis.FOURCC_BC5
	else:
		print("Unknown texture type:\t", hex(tex_type))
		return 0

	raw_image = rapi.imageDecodeDXT(raw_image, width, height, fmt)
	texList.append(NoeTexture(tex_name, width, height, raw_image, noesis.NOESISTEX_RGBA32))

	return 1

