# ================================================================================
# Tomb Raider Anniversary (PC)
# .DRM model viewer
# Noesis script by Dave, 2021 - last updated: 1 August 2021
# Thanks to Raq, Gh0stblade, akderebur, Joschka, AesirHod for providing valuable information for this script
# ================================================================================

# Use with .drm files - no need to extract them first


from inc_noesis import *


def registerNoesisTypes():
	handle = noesis.register("Tomb Raider Anniversary (PC)",".drm")
	noesis.setHandlerTypeCheck(handle, bcCheckType)
	noesis.setHandlerLoadModel(handle, bcLoadModel)
	return 1


def bcCheckType(data):
	bs = NoeBitStream(data)
	file_id = bs.readUInt()

	if file_id != 0x0000000e:
		print("Invalid file")
		return 0
	else:
		return 1


# Read the model data

def bcLoadModel(data, mdlList):
	bs = NoeBitStream(data)

	tex_list, mat_list = ReadTextures(bs)


# Read DRM files

	bs.seek(4)
	entries = bs.readUInt()
	data_start = (entries * 0x14) + 8
	flag = 0

	for a in range(entries):
		bs.seek(a * 0x14 + 8)
		size1 = bs.readUInt()
		entry_type = bs.readUInt()
		bs.readUByte()
		item_entries = bs.readUShort()
		bs.readUByte()
		entry_id = bs.readUInt()

		if entry_type == 0:
			header2 = data_start + (item_entries * 8)
			bs.seek(header2)
			gnc_id = bs.readUInt()

			if gnc_id == 0x04c20453:						# mesh data
				DrawModel(bs, header2, tex_list, mat_list, mdlList)
				flag = 1
#				break							# enable this line to just display first model found

		data_start += size1 + (item_entries * 8)


	if flag == 0:
		print("No meshes found")
		return 0


	return 1



def ReadTextures(bs):
	bs.seek(4)
	entries = bs.readUInt()
	data_start = (entries * 0x14) + 8

	tex_list = []
	mat_list = []

	for a in range(entries):
		bs.seek(a * 0x14 + 8)
		size1 = bs.readUInt()
		entry_type = bs.readUInt()
		bs.readUByte()
		item_entries = bs.readUShort()
		bs.readUByte()
		entry_id = bs.readUInt()

		if entry_type == 5:												# PCD
			material = NoeMaterial("Material_" + str(entry_id), "")
			bs.seek(data_start + 4)
			pcd_type = bs.readUInt()
			pcd_size = bs.readUInt()
			bs.readUInt()
			width = bs.readUShort()
			height = bs.readUShort()

			bs.seek(data_start + 0x18)
			raw_data = bs.readBytes(pcd_size)

			if pcd_type == 0x15:										# RGBA32
				tex1 = NoeTexture("Texture_" + str(entry_id) + ".dds", width, height, raw_data, noesis.NOESISTEX_RGBA32)

			elif pcd_type == 0x31545844:										# DXT1
				tex1 = NoeTexture("Texture_" + str(entry_id) + ".dds", width, height, raw_data, noesis.NOESISTEX_DXT1)

			elif pcd_type == 0x35545844:										# DXT5
				tex1 = NoeTexture("Texture_" + str(entry_id) + ".dds", width, height, raw_data, noesis.NOESISTEX_DXT5)

			else:
				print("Texture format ", hex(pcd_type), " unknown")

			material.setTexture("Texture_" + str(entry_id))
			tex_list.append(tex1)
			mat_list.append(material)

		data_start += size1 + (item_entries * 8)

	return tex_list, mat_list


# Draw one complete model

def DrawModel(bs, header2, tex_list, mat_list, mdlList):
	ctx = rapi.rpgCreateContext()

	bs.seek(header2)
	file_id = bs.readUInt()

	bone_count1 = bs.readUInt()
	bone_count2 = bs.readUInt()
	bone_data = bs.readUInt() + header2
	scaleX = bs.readFloat()
	scaleY = bs.readFloat()
	scaleZ = bs.readFloat()


# Read skeleton data

	bones = []

	for a in range(bone_count1):
		bs.seek(bone_data + (a * 0x40) + 0x20)

		pos = NoeVec3.fromBytes(bs.readBytes(12))
		bs.seek(12, NOESEEK_REL)
		parent_id = bs.readShort()
		matrix = NoeQuat([0, 0, 0, 1]).toMat43()
		matrix[3] = pos
		bones.append(NoeBone(a, "Bone_" + str(a), matrix, None, parent_id))

	bones = rapi.multiplyBones(bones)


# Read vertex data

	bs.seek(header2 + 0x20)
	vert_count = bs.readUInt()
	vert_start = bs.readUInt() + header2

	bs.seek(header2 + 0x58)
	face_info = bs.readUInt() + header2

	vertices = bytearray(vert_count * 12)
	uvs = bytearray(vert_count * 8)
	normals = bytearray(vert_count * 12)
	bone_idx = bytearray(vert_count * 4)
	weights = bytearray(vert_count * 8)

	bs.seek(vert_start)

	for v in range(vert_count):
		bs.seek(vert_start + (v * 0x10))
		vx = bs.readShort() * scaleX
		vy = bs.readShort() * scaleY
		vz = bs.readShort() * scaleZ

		nx = bs.readByte() / 127
		ny = bs.readByte() / 127
		nz = bs.readByte() / 127
		bs.readByte()								# padding byte

		bone_id = bs.readUShort()
		uvx = bs.readUShort() << 16							# convert to correct float values
		uvy = bs.readUShort() << 16

		if bone_id > (bone_count1-1):
			bs.seek(bone_data + (bone_id * 0x40) + 0x38)
			bone_id = bs.readUShort()
			bone_id2 = bs.readUShort()
			weight1 = bs.readFloat()
			weight2 = 1 - weight1
			struct.pack_into("<HH", bone_idx, v * 4, bone_id, bone_id2)
			struct.pack_into("<ff", weights, v * 8, weight2, weight1)
		else:
			struct.pack_into("<HH", bone_idx, v * 4, bone_id, 0)
			struct.pack_into("<ff", weights, v * 8, 1, 0)

# Transform vertices to bone position without using rpgSkinPreconstructedVertsToBones

		vertpos = bones[bone_id].getMatrix().transformPoint([vx, vy, vz])
		normpos = bones[bone_id].getMatrix().transformNormal([nx, ny, nz])

		struct.pack_into("<fff", vertices, v * 12, *vertpos)
		struct.pack_into("<II", uvs, v*8, uvx, uvy)
		struct.pack_into("<fff", normals, v*12, *normpos)

	flag = 0
	current_mesh = face_info
	mesh_num = 0

	rapi.rpgBindPositionBuffer(vertices, noesis.RPGEODATA_FLOAT, 12)
	rapi.rpgBindNormalBuffer(normals, noesis.RPGEODATA_FLOAT, 12)
	rapi.rpgBindUV1Buffer(uvs, noesis.RPGEODATA_FLOAT, 8)
	rapi.rpgBindBoneIndexBuffer(bone_idx, noesis.RPGEODATA_USHORT, 4, 2)
	rapi.rpgBindBoneWeightBuffer(weights, noesis.RPGEODATA_FLOAT, 8, 2)

	while flag == 0:
		bs.seek(current_mesh)
		face_count = bs.readUShort()

		if face_count == 0:								# no more sub-meshes
			break

		misc1 = bs.readUShort()
		tex_id = bs.readUShort() & 0x1FFF						# bits 0-12
		misc3 = bs.readUShort()
		misc4 = bs.readUShort()
		misc5 = bs.readUShort()
		misc6 = bs.readUShort()
		misc7 = bs.readUShort()

		current_mesh = bs.readUInt() + header2					# next face section
		faces = bs.readBytes(face_count * 2)

		rapi.rpgSetMaterial("Material_" + str(tex_id))
		rapi.rpgSetName("Mesh_" + str(mesh_num))
		rapi.rpgCommitTriangles(faces, noesis.RPGEODATA_USHORT, face_count, noesis.RPGEO_TRIANGLE)
		mesh_num += 1

	try:
		mdl = rapi.rpgConstructModel()
	except:
		mdl = NoeModel()

	mdl.setModelMaterials(NoeModelMaterials(tex_list, mat_list))
	mdl.setBones(bones)
	mdlList.append(mdl)

	return 1


