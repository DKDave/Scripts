# Power Rangers Super Samurai (XBox 360)
# Noesis script by DKDave, 2024

# Currently reads the character models (.NDXR) and their textures (.NTXR)

# TO DO:
# Other mesh files with slightly different formats



from inc_noesis import *


def registerNoesisTypes():
	handle = noesis.register("Power Rangers Super Samurai (XBox 360)",".ndxr")
	noesis.setHandlerTypeCheck(handle, bcCheckType)
	noesis.setHandlerLoadModel(handle, bcLoadModel)
	return 1


# Check file type

def bcCheckType(data):
	bs = NoeBitStream(data, NOE_BIGENDIAN)
	bs.seek(0)
	file_id = bs.readUInt()

	if file_id == 0x4e445852:
		return 1
	else:
		print("Invalid file")
		return 0


# Read the model data

def bcLoadModel(data, mdlList):
	bs = NoeBitStream(data, NOE_BIGENDIAN)
	ctx = rapi.rpgCreateContext()
	rapi.rpgSetOption(noesis.RPGOPT_BIGENDIAN, 1)

	curr_folder = rapi.getDirForFilePath(rapi.getInputName()).lower()
	curr_file = rapi.getLocalFileName(rapi.getInputName()).lower()
	tex_archive = curr_file.replace(".ndxr", ".ntxr")


# Read texture data

	mat_list = []
	tex_list = []

	tex_check = rapi.checkFileExists(curr_folder + tex_archive)

	if tex_check == 1:
		tx = NoeBitStream(rapi.loadIntoByteArray(curr_folder + tex_archive), NOE_BIGENDIAN)

		tx.seek(6)
		tx_count = tx.readUShort()
		offset = 0x10

		for t in range(tx_count):
			tx.seek(offset)
			total_size = tx.readUInt()

			tx.seek(offset + 0x10)
			mip_count = tx.readUShort()
			tex_type = tx.readUShort()
			width = tx.readUShort()
			height = tx.readUShort()

			if mip_count > 1:
				mip_info_size = ((mip_count * 4) + 15) & 0xFFFFFFF0
				tx.seek(offset + 0x30)
				data_size = tx.readUInt()
			else:
				mip_info_size = 0
				tx.seek(offset + 8)
				data_size = tx.readUInt()

			data_start = offset + 0x50 + mip_info_size

			tx.seek(offset + mip_info_size + 0x48)
			tex_id = tx.readUInt()
			tex_name = "tex_" + str(tex_id)

			tx.seek(data_start)
			raw_image = tx.readBytes(data_size)
			raw_image = rapi.swapEndianArray(raw_image, 2)

			if tex_type == 0:
				raw_image = rapi.imageDecodeDXT(raw_image, width, height, noesis.NOESISTEX_DXT1)
			elif tex_type == 1:
				raw_image = rapi.imageDecodeDXT(raw_image, width, height, noesis.NOESISTEX_DXT3)
			elif tex_type == 7:
				raw_image = rapi.imageDecodeRaw(raw_image, width, height, "b5g6r5")
			elif tex_type == 19:
				raw_image = rapi.imageDecodeRaw(raw_image, width, height, "a8b8g8r8")
			else:
				print("Unknown texture type:\t", tex_type, "\t", hex(offset), "\t", hex(data_size))

			tex1 = NoeTexture(tex_name, width, height, raw_image, noesis.NOESISTEX_RGBA32)
			tex_list.append(tex1)

			offset += total_size

	else:
		print("Texture archive not found.")


	bs.seek(0x0a)
	mesh_count = bs.readUShort()
	unk1 = bs.readUInt()
	mesh_info = 0x30
	face_data = bs.readUInt() + mesh_info
	uv_data = bs.readUInt() + face_data
	vert_data = bs.readUInt() + uv_data
	name_data = bs.readUInt() + vert_data
	mat_num = 0

	for m in range(mesh_count):
		bs.seek(mesh_info + (m * 0x30) + 0x20)
		name_offset = bs.readUInt()
		bs.seek(6, 1)
		submesh_count = bs.readUShort()
		submesh_info = bs.readUInt()
		bs.seek(name_data + name_offset)
		mesh_name = bs.readString()

		for s in range(submesh_count):
			bs.seek(submesh_info + (s * 0x30))
			face_off = bs.readUInt() + face_data
			uv_off = bs.readUInt() + uv_data
			vert_off = bs.readUInt() + vert_data
			vert_count = bs.readUShort()
			vert_type = bs.readUByte()						# 0x13 = stride 0x60, 0x11 = stride 0x40 ??
			bs.readUByte()
			mat_info = bs.readUInt()
			bs.seek(0x0c, 1)
			face_count = bs.readUShort()

			if vert_type == 0x13:
				stride = 0x60
			elif vert_type == 0x11:
				stride = 0x40
			else:
				print("Unknown vertex type:\t", hex(vert_type))
				stride = -1

			bs.seek(vert_off)
			vertices = bs.readBytes(vert_count * stride)
			bs.seek(uv_off)
			uvs = bs.readBytes(vert_count * 4)
			bs.seek(face_off)
			faces = bs.readBytes(face_count * 2)

			material = NoeMaterial("Mat_" + str(mat_num), "")
			bs.seek(mat_info + 0x0a)
			tex_parts = bs.readUShort()

			for p in range(tex_parts):
				bs.seek(mat_info + 0x20 + (p * 0x18))
				tex_id = bs.readUInt()

				if p == 0:
					material.setTexture("Tex_" + str(tex_id))
				elif p == 1:
					material.setNormalTexture("Tex_" + str(tex_id))
				elif p == 2:
					material.setSpecularTexture("Tex_" + str(tex_id))

			mat_list.append(material)

			rapi.rpgSetMaterial("Mat_" + str(mat_num))
			rapi.rpgSetName(mesh_name + "_" + str(s))
			rapi.rpgSetStripEnder(0xFFFF)
			rapi.rpgBindPositionBuffer(vertices, noesis.RPGEODATA_FLOAT, stride)
			rapi.rpgBindUV1Buffer(uvs, noesis.RPGEODATA_HALFFLOAT, 4)
			rapi.rpgBindNormalBufferOfs(vertices, noesis.RPGEODATA_FLOAT, stride, 0x10)
			rapi.rpgCommitTriangles(faces, noesis.RPGEODATA_USHORT, face_count, noesis.RPGEO_TRIANGLE_STRIP)

			mat_num += 1

	try:
		mdl = rapi.rpgConstructModel()
	except:
		mdl = NoeModel()

	mdl.setModelMaterials(NoeModelMaterials(tex_list, mat_list))
	mdlList.append(mdl)

	return 1


