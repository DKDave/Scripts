# ================================================================================
# Once Human Beta (2023)
# .MESH viewer
# Noesis script by DKDave, 2023 - last updated: 6 January 2024
# ================================================================================

# SET BASE_FOLDER TO YOUR OWN MAIN FOLDER FIRST


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

	global base_folder
	base_folder = ""								# SET THIS BEFORE USING THE SCRIPT

	if base_folder == "":
		print("ERROR:\tBase folder has not yet been set!")
		return 0

	rapi.rpgSetOption(noesis.RPGOPT_SWAPHANDEDNESS, 1)

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
	submesh_info = []
	mat_files = []

	while True:
		text = gm.readline().decode("ascii").replace("\x0a", "")

		if "<SubMesh>" in text:
			while True:
				subtext = gm.readline().decode("ascii").replace("\x0a", "")

				if "<Sub" in subtext:
					submesh_count += 1

				if "Name=" in subtext:
					submesh_name = subtext.replace("\t\t\tName=", "").replace("\x22", "").replace(" />", "")

				if "MtlIdx=" in subtext:
					submesh_mat = subtext.replace("\t\t\tMtlIdx=\x22", "").replace("\x22", "")	

				if "/>" in subtext:
					submesh_info.append([submesh_name, int(submesh_mat)])

				if "</SubMesh>" in subtext:
					break

		if "</NeoX>" in text:
			break

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
				material_file = text.replace("\t\t\tFileName=\x22", "").replace("\x22 />", "")
				material_file = material_file.replace("/", "\\")
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
	vert_data = submesh_header + (submesh_count * 10) + 10

	bs.seek(submesh_header)
	colour_count = 0
	uv_size = 0
	colour_size = 0
	vert_off = 0
	uv_off = 0
	face_off = 0

	for a in range(submesh_count):
		temp1 = bs.readUInt()								# vertex count
		temp2 = bs.readUInt()								# triangle count
		temp3 = bs.readUByte()								# Number of UV sets for this submesh
		temp4 = bs.readUByte()								# flag if colours are present for this submesh

		submesh_info2.append([temp1, temp2, temp3, temp4, vert_off, uv_off, face_off])

		if temp4 == 1:
			colour_size += (temp1 * 4)

		vert_off += temp1
		uv_off += temp1 * temp3
		uv_size += (temp1 * temp3 * 8)
		face_off += (temp2 * 6)


	bs.readUShort()										# Always 1 ?
	total_verts = bs.readUInt()
	total_faces = bs.readUInt()

	norm_data = vert_data + (total_verts * 12)
	bs.readUShort()										# Always 1 ?
	misc_data = norm_data + (total_verts * 12) + 2
	face_data = misc_data + (total_verts * 12)
	uv_data = face_data + (total_faces * 6)
	colour_data = uv_data + uv_size

	if bone_flag == 1:
		bone_data = colour_data + colour_size
		bs.seek(bone_data)
		bone_idx = bs.readBytes(total_verts * 8)							# 4 UShorts
		bone_weights = bs.readBytes(total_verts * 0x10)						# 4 Floats
		rapi.rpgBindBoneIndexBuffer(bone_idx, noesis.RPGEODATA_SHORT, 8, 4)
		rapi.rpgBindBoneWeightBuffer(bone_weights, noesis.RPGEODATA_FLOAT, 0x10, 4)

	for a in range(submesh_count):
		vert_count = submesh_info2[a][0]
		face_count = submesh_info2[a][1]
		uv_flag = submesh_info2[a][2]

		bs.seek(vert_data + (submesh_info2[a][4] * 12))
		vertices = bs.readBytes(vert_count * 12)

		bs.seek(norm_data + (submesh_info2[a][4] * 12))
		normals = bs.readBytes(vert_count * 12)

		if submesh_info2[a][2] == 1:
			bs.seek(uv_data + (submesh_info2[a][5] * 8))
			uvs = bs.readBytes(vert_count * 8)
		else:										# first block of 8 bytes per vertex is not UVs ?
			bs.seek(uv_data + (submesh_info2[a][5] * 8) + (vert_count *8))
			uvs = bs.readBytes(vert_count * 8)

		rapi.rpgBindPositionBuffer(vertices, noesis.RPGEODATA_FLOAT, 12)
		rapi.rpgBindNormalBuffer(normals, noesis.RPGEODATA_FLOAT, 12)
		rapi.rpgBindUV1Buffer(uvs, noesis.RPGEODATA_FLOAT, 8)

		faces = bytearray(face_count * 6)
		bs.seek(face_data + submesh_info2[a][6])

# Recalculate face index values for this submesh

		for f in range(face_count * 3):
			idx = bs.readUShort() - submesh_info2[a][4]
			struct.pack_into("<H", faces, f * 2, idx)

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


# Create material from .mtl file and load relevant textures

def CreateMaterial(bs, curr_folder, mat_filename, tex_list, mat_list, mat_num):

	check = rapi.checkFileExists(base_folder + mat_filename)

	if check == 0:
		print("Material file " + base_folder + mat_filename + " not found.")
		return tex_list, mat_list

	mf = open(base_folder + mat_filename, "rb")

	material = NoeMaterial("Material_" + str(mat_num), "")

	while True:
		text = mf.readline().decode("ascii")

		if "<Material" in text:
			mat_text = mf.readline().decode("ascii")

			if "</Material>" in mat_text:
				break

		if "<AlbedoMap" in text:
			diffuse_name = mf.readline().decode("ascii").replace("\t\t\t\tValue=\x22", "").replace("\x22 />\x0a", "")
			diffuse_name = diffuse_name.replace(".png", ".pvr").replace(".tga", ".pvr")

			check = rapi.checkFileExists(base_folder + diffuse_name)

			if check == 1:
				tex_file = NoeBitStream(rapi.loadIntoByteArray(base_folder + diffuse_name))
				tex = ProcessPVR(tex_file, diffuse_name)
				tex.name = diffuse_name
				tex_list.append(tex)
				material.setTexture(diffuse_name)
			else:
				print(diffuse_name, " not found.")

		if "<NormalMap" in text:
			normal_name = mf.readline().decode("ascii").replace("\t\t\t\tValue=\x22", "").replace("\x22 />\x0a", "")
			normal_name = normal_name.replace(".png", ".pvr").replace(".tga", ".pvr")

			check = rapi.checkFileExists(base_folder + normal_name)

			if check == 1:
				tex_file = NoeBitStream(rapi.loadIntoByteArray(base_folder + normal_name))
				tex = ProcessPVR(tex_file, normal_name)
				tex.name = normal_name
				tex_list.append(tex)
				material.setNormalTexture(normal_name)
			else:
				print(normal_name, " not found.")

		if "<ControlMap" in text:
			control_name = mf.readline().decode("ascii").replace("\t\t\t\tValue=\x22", "").replace("\x22 />\x0a", "")
			control_name = control_name.replace(".png", ".pvr").replace(".tga", ".pvr")

			check = rapi.checkFileExists(base_folder + control_name)

			if check == 1:
				tex_file = NoeBitStream(rapi.loadIntoByteArray(base_folder + control_name))
				tex = ProcessPVR(tex_file, control_name)
				tex.name = control_name
				tex_list.append(tex)
#				material.set????Texture(control_name)					# which type ?
			else:
				print(control_name, " not found.")

		if "<FeatureMap" in text:
			feature_name = mf.readline().decode("ascii").replace("\t\t\t\tValue=\x22", "").replace("\x22 />\x0a", "")
			feature_name = feature_name.replace(".png", ".pvr").replace(".tga", ".pvr")

			check = rapi.checkFileExists(base_folder + feature_name)

			if check == 1:
				tex_file = NoeBitStream(rapi.loadIntoByteArray(base_folder + feature_name))
				tex = ProcessPVR(tex_file, feature_name)
				tex.name = feature_name
				tex_list.append(tex)
				material.setSpecularTexture(feature_name)
			else:
				print(feature_name, " not found.")


		if "</NeoX>" in text:
			break

		if "</Material>" in text:								# End of current material definition
			mat_list.append(material)
			mat_num += 1

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
		raw_image = rapi.imageDecodeRaw(raw_image, width, height, "a8g8b8r8")				# Normal textures need channels swapping

	tex1 = NoeTexture(tex_name, width, height, raw_image, noesis.NOESISTEX_RGBA32)

	return tex1

