# LOTR: Fellowship Of The Ring (XBox)
# Noesis script by DKDave, 2025

# View textures in XPR archives

# TO DO:
# Process names correctly - some archives have more files than names


from inc_noesis import *


def registerNoesisTypes():
	handle = noesis.register("LOTR: Fellowship Of The Ring Textures (Xbox)",".xpr")
	noesis.setHandlerTypeCheck(handle, bcCheckType)
	noesis.setHandlerLoadModel(handle, bcLoadModel)
	return 1


# Check file type

def bcCheckType(data):
	bs = NoeBitStream(data)

	bs.seek(0)
	check = bs.read(4)

	if check != b'XPR0':
		return 0
	else:
		return 1


# Read the texture data

def bcLoadModel(data, mdlList):
	bs = NoeBitStream(data)
	ctx = rapi.rpgCreateContext()

	curr_file = rapi.getLocalFileName(rapi.getInputName()).lower()
	basename = curr_file.replace(".xpr", "")

	dimensions = {2: 4, 3: 8, 4:16, 5: 32, 6: 64, 7: 128, 8: 256, 9: 512, 10: 1024, 11: 2048}
	formats = [0x0c, 0x0e, 0x12, 0x1e]

	file_size = len(data)
	tex_list = []

	bs.seek(4)
	table_size = bs.readUInt()
	data_start = bs.readUInt()
	entry = 0x0c

	img_num = 0

	while True:
		bs.seek(entry + (img_num * 0x14))
		misc1 = bs.readUShort()

		if misc1 != 1:
			break

		misc2 = bs.readUShort()						# Mip count? (always 4?)
		offset = bs.readUInt() + data_start
		bs.readUInt()							# Always 0 ?
		unk1 = bs.readUByte()						# Always 0x29 ?
		pixel_format = bs.readUByte()						# 0x0c = DXT1, 0x0e = DXT3, 0x12 = BGRA32, 0x1e = BGRx32
		info = bs.readUShort()						# dimensions + other info
		info2 = bs.readUInt()						# dimensions if 0 in info value

		if pixel_format not in formats:
			print("Unknown pixel format:\t", pixel_format)

		else:
			print("Format:\t", pixel_format)
			image_name = basename + "_" + str(img_num)

			width_temp = (info & 0xf0) >> 4
			height_temp = (info & 0xf00) >> 8

			if width_temp == 0:
				width = ((info2 & 0xfff) + 1)
				mod = width % 16

				if mod != 0:
					width += (16 - mod)				# Actual pixel width (padded to multiple of 16 bytes)

				height = ((info2 & 0xfff000) >> 12) + 1

			else:
				width = dimensions[width_temp]
				height = dimensions[height_temp]

			bs.seek(offset)

			if pixel_format == 0x0c:
				raw_image = bs.readBytes((width * height) // 2)
				new_image = NoeTexture(image_name, width, height, raw_image, noesis.NOESISTEX_DXT1)

			elif pixel_format == 0x0e:
				raw_image = bs.readBytes(width * height)
				new_image = NoeTexture(image_name, width, height, raw_image, noesis.NOESISTEX_DXT3)

			elif pixel_format == 0x12:
				raw_image = bs.readBytes(width * height * 4)
				new_image = rapi.imageDecodeRaw(raw_image, width, height, "b8 g8 r8 a8")
				new_image = NoeTexture(image_name, width, height, new_image, noesis.NOESISTEX_RGBA32)

			elif pixel_format == 0x1e:
				raw_image = bs.readBytes(width * height * 4)
				new_image = rapi.imageDecodeRaw(raw_image, width, height, "b8 g8 r8 p8")
				new_image = NoeTexture(image_name, width, height, new_image, noesis.NOESISTEX_RGBA32)

			tex_list.append(new_image)

		img_num += 1


	try:
		mdl = rapi.rpgConstructModel()
	except:
		mdl = NoeModel()

	mdl.setModelMaterials(NoeModelMaterials(tex_list, []))
	mdlList.append(mdl)

	return 1


