# Fancy Pants Adventures (PS3 / Android / X360)
# Texture Viewer
# Noesis script by DKDave, 2023 (last updated 31 March 2024)

# XBox360 textures use the same texture types, but are tiled, so change the x360 = 0 to x360 = 1 if you want to extract those
# Update 29 March: Fixed dimension issues


from inc_noesis import *

def registerNoesisTypes():
	handle = noesis.register("Fancy Pants Adventures Textures (PS3/Android/X360)",".lvl;.bgd;.tex")
	noesis.setHandlerTypeCheck(handle, CheckType)
	noesis.setHandlerLoadModel(handle, bcLoadModel)
	return 1


# Check file type

def CheckType(data):
	bs = NoeBitStream(data)
	return 1


def bcLoadModel(data, mdlList):
	bs = NoeBitStream(data)

	check = bs.readUInt()

	if check == 0x52535243:
		bs = NoeBitStream(data, NOE_BIGENDIAN)

	x360 = 0										# 0 = for PS3/Android, 1 = XBox360

	tex_list = []

	offset = 0
	file_end = len(data)
	tex_count = 0

	while True:
		if offset == file_end:
			break

		bs.seek(offset + 4)
		type = bs.readBytes(4).decode("ascii")
		bs.readUInt()
		data_size = bs.readUInt() + 0x20

		if type == "TXET" or type == "TEXT":
			bs.seek(offset + 0x20)
			tex_fmt = bs.readUInt()
			width = bs.readUInt()
			height = bs.readUInt()
			bs.seek(offset + 0x44)

			tex_data_size = bs.readUInt()
			bs.seek(offset + 0x60)
			raw_image = bs.readBytes(tex_data_size)

#			print("TYPE:\t", tex_fmt, "\t", width, "\t", height)

			if tex_fmt == 3:
				raw_image = rapi.imageDecodeRaw(raw_image, width, height, "b5g6r5")
				raw_image = rapi.imageFlipRGBA32(raw_image, width, height, 0, 1)
				tex = NoeTexture("Texture_" + str(tex_count), width, height, raw_image, noesis.NOESISTEX_RGBA32)
				tex_list.append(tex)

			elif tex_fmt == 0x14:
				if width %16 > 0:
					width += 16 - (width %16)

				if height %16 > 0:
					height += 16 - (height %16)

				if x360 == 1:
					raw_image = rapi.swapEndianArray(raw_image, 2)
					raw_image = rapi.imageUntile360DXT(raw_image, width, height, 16)

				raw_image = rapi.imageDecodeDXT(raw_image, width, height, noesis.FOURCC_BC3)
				raw_image = rapi.imageFlipRGBA32(raw_image, width, height, 0, 1)
				tex = NoeTexture("Texture_" + str(tex_count), width, height, raw_image, noesis.NOESISTEX_RGBA32)
				tex_list.append(tex)

			elif tex_fmt == 0x15:
				raw_image = rapi.imageDecodeRaw(raw_image, width, height, "a4b4g4r4")
				raw_image = rapi.imageFlipRGBA32(raw_image, width, height, 0, 1)
				tex = NoeTexture("Texture_" + str(tex_count), width, height, raw_image, noesis.NOESISTEX_RGBA32)
				tex_list.append(tex)

			elif tex_fmt == 6:
				if width %4 > 0:
					width += 4 - (width %4)

				if height %4 > 0:
					height += 4 - (height %4)

				if x360 == 1:
					raw_image = rapi.swapEndianArray(raw_image, 4)
					raw_image = rapi.imageUntile360Raw(raw_image, width, height, 4)
					raw_image = rapi.imageSwapChannelRGBA32(raw_image, 0, 2)

				raw_image = rapi.imageFlipRGBA32(raw_image, width, height, 0, 1)
				tex = NoeTexture("Texture_" + str(tex_count), width, height, raw_image, noesis.NOESISTEX_RGBA32)
				tex_list.append(tex)

			else:
				print("Unknown texture format: ", tex_fmt)

			tex_count += 1

		offset += data_size

	try:
		mdl = rapi.rpgConstructModel()
	except:
		mdl = NoeModel()

	mdl.setModelMaterials(NoeModelMaterials(tex_list, []))
	mdlList.append(mdl)


	return 1
