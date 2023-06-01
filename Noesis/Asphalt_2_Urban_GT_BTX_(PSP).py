# ================================================================================
# Asphalt 2: Urban GT (PSP)
# BTX texture viewer
# Noesis script by DKDave, 2023
# ================================================================================


from inc_noesis import *

def registerNoesisTypes():
	handle = noesis.register("Asphalt 2: Urban GT (PSP)",".btx")
	noesis.setHandlerTypeCheck(handle, bcCheckType)
	noesis.setHandlerLoadModel(handle, bcLoadModel)
	return 1


# Check file type

def bcCheckType(data):
	bs = NoeBitStream(data)
	check = bs.readUInt()

	if check != 0x5854422e:								# ".BTX"
		return 0
	else:
		return 1


# Read the texture data

def bcLoadModel(data, mdlList):
	bs = NoeBitStream(data)

	curr_file = rapi.getLocalFileName(rapi.getInputName()).lower()
	basename = curr_file.replace(".btx", "")

	tex_list = []

	bs.seek(4)
	tex_type = bs.readUInt()								# 0, 6 or 7
	width = bs.readUInt()
	height = bs.readUInt()

	if tex_type == 0:									# RGBA32
		bs.seek(0x28)
		raw_image = bs.readBytes(width * height * 4)
		raw_image = rapi.imageUntwiddlePSP(raw_image, width, height, 32)
		raw_image = rapi.imageDecodeRaw(raw_image, width, height, "r8g8b8a8")

	elif tex_type == 6:									# 8-bit
		bs.seek(0x28)
		pal = bs.readBytes(0x400)
		raw_image = bs.readBytes(width * height)
		raw_image = rapi.imageUntwiddlePSP(raw_image, width, height, 8)
		raw_image = rapi.imageDecodeRawPal(raw_image, pal, width, height, 8, "r8g8b8a8")

	elif tex_type == 7:									# 4-bit
		bs.seek(0x28)
		pal = bs.readBytes(0x40)
		raw_image = bs.readBytes((width * height) // 2)
		raw_image = rapi.imageUntwiddlePSP(raw_image, width, height, 4)
		raw_image = rapi.imageDecodeRawPal(raw_image, pal, width, height, 4, "r8g8b8a8")

	else:
		print("Unknown type:", tex_type)

	tex1 = NoeTexture(basename, width, height, raw_image, noesis.NOESISTEX_RGBA32)
	tex_list.append(tex1)

	mdl = NoeModel()
	mdl.setModelMaterials(NoeModelMaterials(tex_list, []))
	mdlList.append(mdl)

	return 1

