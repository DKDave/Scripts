# ================================================================================
# Once Human Beta (2023)
# .MESH viewer
# Noesis script by DKDave, 2023 - last updated: 1 January 2024
# ================================================================================

# Make sure that .mesh, .gim, .mtgm .mtl are all in the same folder, with textures in a "tex" subfolder

# TO DO:
# Process other texture types (control/f/r)


from inc_noesis import *


def registerNoesisTypes():
	handle = noesis.register("Once Human (Beta)",".mesh")
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

	curr_folder = rapi.getDirForFilePath(rapi.getInputName()).lower()
	curr_file = rapi.getLocalFileName(rapi.getInputName()).lower()

	tex_list = []
	mat_list = []


# Get some submesh information from the .gim file

	gim_file = curr_file.replace(".mesh", ".gim")

	check = rapi.checkFileExists(curr_folder + gim_file)

	if check == 0:
		print("No .gim file found")
		return 1

	gm = open(curr_folder + gim_file, "rb")
	submesh_count = 0
	submesh_flag = 0
	submesh_info = []
	mat_files = []
	flag1 = 0
	flag2 = 0

	while True:
		text = gm.readline().decode("ascii").replace("\x0a", "")

		if "<Sub" in text and submesh_flag == 1:
			submesh_count += 1

		if "Name=" in text:
			submesh_name = text.replace("\t\t\tName=", "")
			flag1 = 1

		if "MtlIdx=" in text:
			submesh_mat = text.replace("\t\t\tMtlIdx=\x22", "").replace("\x22", "")	
			flag2 = 1

		if "<SubMesh" in text:
			submesh_flag = 1

		if "</SubMesh>" in text:
			break

		if flag1 == 1 and flag2 == 1:
			submesh_info.append([submesh_name, int(submesh_mat)])
			flag1 = 0
			flag2 = 0

	gm.close()


# Read mtg material file and create a list of .mtl files

	mtg_file = curr_file.replace(".mesh", ".mtg")

	check = rapi.checkFileExists(curr_folder + mtg_file)

	if check == 0:
		print("No .mtg file found - no materials will be available")
		return 1

	else:
		mtg = open(curr_folder + mtg_file, "rb")

		while True:
			text = mtg.readline().decode("ascii").replace("\x0a", "")

			if "FileName=" in text:
				material_file = text.replace("\t\t\tFileName=\x22", "")
				material_file = material_file.replace("\x22 />", "").split("/")
				material_file = material_file[len(material_file)-1]
				mat_files.append(material_file)

			if "</NeoX>" in text:
				break

		mtg.close()

		mat_num = 0

		for a in mat_files:
			tex_list, mat_list = CreateMaterial(bs, curr_folder, a, tex_list, mat_list, mat_num)
			mat_num += 1


# Read Skeleton Data (if it exists)

	bs.seek(8)
	bone_flag = bs.readUInt()
	bones = []

	if bone_flag == 1:
		bone_count = bs.readUShort()
		bone_names = (bone_count * 2) + 0x0e
		bone_data = bone_names + (bone_count * 0x20) + 1 + (bone_count * 0x1c)

		for a in range(bone_count):
			bs.seek(0x0e + (a * 2))
			parent = bs.readShort()
			bs.seek(bone_names + (a * 0x20))
			bone_name = bs.readString()
			bs.seek(bone_data + (a * 0x40))
			matrix = NoeMat44.fromBytes(bs.readBytes(0x40)).toMat43()
			bones.append(NoeBone(a, bone_name, matrix, None, parent))


# Read Submesh Info

	submesh_info2 = []

	bs.seek(len(data) - 14)
	submesh_header = bs.readUInt()

	bs.seek(submesh_header)
	colour_count = 0

	for a in range(submesh_count):
		temp1 = bs.readUInt()
		temp2 = bs.readUInt()
		temp3 = bs.readUByte()								# flag for ?
		temp4 = bs.readUByte()								# flag if colours are present for this submesh
		submesh_info2.append([temp1, temp2, temp3, temp4])

		if temp4 == 1:
			colour_count += temp1							# vertex count for colours

	bs.readUShort()
	total_verts = bs.readUInt()
	total_faces = bs.readUInt()

	vertices = bs.readBytes(total_verts * 12)
	normals = bs.readBytes(total_verts * 12)
	bs.readUShort()
	misc_buffer = bs.readBytes(total_verts * 12)
	face_data = bs.tell()
	bs.seek(total_faces * 6, 1)									# Skip face data for now
	uvs = bs.readBytes(total_verts * 8)
	colours = bs.readBytes(colour_count * 4)							# Vertex colours

	if bone_flag == 1:
		bone_idx = bs.readBytes(total_verts * 8)							# 4 Shorts
		bone_weights = bs.readBytes(total_verts * 0x10)						# 4 Floats
		rapi.rpgBindBoneIndexBuffer(bone_idx, noesis.RPGEODATA_SHORT, 8, 4)
		rapi.rpgBindBoneWeightBuffer(bone_weights, noesis.RPGEODATA_FLOAT, 0x10, 4)

	rapi.rpgBindPositionBuffer(vertices, noesis.RPGEODATA_FLOAT, 12)
	rapi.rpgBindNormalBuffer(normals, noesis.RPGEODATA_FLOAT, 12)
	rapi.rpgBindUV1Buffer(uvs, noesis.RPGEODATA_FLOAT, 8)

	face_start = 0

	for a in range(submesh_count):
		face_count = submesh_info2[a][1]
		bs.seek(face_data + (face_start * 6))
		faces = bs.readBytes(face_count * 6)
		face_start += face_count

		rapi.rpgSetName(submesh_info[a][0])
		rapi.rpgSetMaterial("Material_" + str(submesh_info[a][1]))
		rapi.rpgCommitTriangles(faces, noesis.RPGEODATA_USHORT, face_count * 3, noesis.RPGEO_TRIANGLE, 1)

	try:
		mdl = rapi.rpgConstructModel()
	except:
		mdl = NoeModel()

	mdl.setModelMaterials(NoeModelMaterials(tex_list, mat_list))

	if bone_flag == 1:
		mdl.setBones(bones)

	mdlList.append(mdl)

	return 1


# Create materials from .mtl file and load textures from "tex" subfolder

def CreateMaterial(bs, curr_folder, mat_filename, tex_list, mat_list, mat_num):

	check = rapi.checkFileExists(curr_folder + mat_filename)

	if check == 0:
		print("Material file " + mat_filename + " not found.")
		return tex_list, mat_list

	mf = open(curr_folder + mat_filename, "rb")

	while True:
		text = mf.readline().decode("ascii")

		if "<Material\x0a" in text:								# New material definition
			material = NoeMaterial("Material_" + str(mat_num), "")

		if "<AlbedoMap" in text:
			diffuse_name = mf.readline().decode("ascii").replace("\t\t\t\tValue=\x22", "")
			diffuse_name = diffuse_name.replace("\x22 \x2f>\x0a", "").split("/")
			diffuse_name = diffuse_name[len(diffuse_name)-1].replace(".png", ".pvr").replace(".tga", ".pvr")

			check = rapi.checkFileExists(curr_folder + "tex\\" + diffuse_name)

			if check == 1:
				tex_file = NoeBitStream(rapi.loadIntoByteArray(curr_folder + "tex\\" + diffuse_name))
				tex = ProcessPVR(tex_file, diffuse_name)
				tex.name = diffuse_name
				tex_list.append(tex)
				material.setTexture(diffuse_name)
			else:
				print(diffuse_name, " not found.")

		if "<NormalMap" in text:
			normal_name = mf.readline().decode("ascii").replace("\t\t\t\tValue=\x22", "")
			normal_name = normal_name.replace("\x22 \x2f>\x0a", "").split("/")
			normal_name = normal_name[len(normal_name)-1].replace(".png", ".pvr").replace(".tga", ".pvr")

			check = rapi.checkFileExists(curr_folder + "tex\\" + normal_name)

			if check == 1:
				tex_file = NoeBitStream(rapi.loadIntoByteArray(curr_folder + "tex\\" + normal_name))
				tex = ProcessPVR(tex_file, normal_name)
				tex.name = normal_name
				tex_list.append(tex)
				material.setNormalTexture(normal_name)
			else:
				print(normal_name, " not found.")

		if "</Material>" in text:								# End of current material definition
			mat_list.append(material)
			mat_num += 1

		if "</NeoX>" in text:
			break

	mf.close()

	return tex_list, mat_list


# Decode PVR texture file

def ProcessPVR(pvr, tex_name):
	pvr.seek(8)
	tex_type = pvr.readUInt()
	pvr.seek(0x18)
	width = pvr.readUInt()
	height = pvr.readUInt()
	data_size = pvr.getSize() - 0x34
	pvr.seek(0x34)
	raw_image = pvr.readBytes(data_size)

	if tex_type == 7:
		raw_image = rapi.imageDecodeDXT(raw_image, width, height, noesis.NOESISTEX_DXT1)

	elif tex_type == 0x0b:
		raw_image = rapi.imageDecodeDXT(raw_image, width, height, noesis.NOESISTEX_DXT5)

	else:
		print("Unknown texture type:\t", tex_type)
		return 0

	if "_normal" in tex_name or "_n" in tex_name:
		raw_image = rapi.imageDecodeRaw(raw_image, width, height, "a8g8b8r8")

	tex1 = NoeTexture("Name", width, height, raw_image, noesis.NOESISTEX_RGBA32)

	return tex1

