# Neversoft RLE (PSX)
# Decompress .rle images
# Noesis script by DKDave, 2021

# Should work for: Spider-Man, Spider-Man 2, Apocalypse


from inc_noesis import *

def registerNoesisTypes():
	handle = noesis.register("Neversoft RLE",".rle")
	noesis.setHandlerTypeCheck(handle, bcCheckType)
	noesis.setHandlerLoadRGBA(handle, bcLoadRGBA)
	return 1


# Check file type

def bcCheckType(data):
	bs = NoeBitStream(data)
	file_id = bs.readBytes(8).decode("utf-8")

	if file_id == "_RLE_16_":
		return 1
	else:
		return 0


# Read the image data

def bcLoadRGBA(data, texList):
	bs = NoeBitStream(data)

	test1 = bs.tell()
	magic = b'_16_'
	offset = data.find(magic, test1)
	print(hex(offset))


	bs.seek(8)
	dec_size = bs.readUInt()
	new_size = 0

	new_image = bytearray()

	while new_size < dec_size:
		command = bs.readUShort()
		count = command & 0x7fff
		command = command >> 15

		if command == 0:							# copy xx colours from file
			for a in range(count):
				new_image += struct.pack("<H", bs.readUShort())

		if command == 1:							# repeat colour xx times
			colour = bs.readUShort()

			for a in range(count):
				new_image += struct.pack("<H", colour)

		new_size += count * 2

	width = 512
	height = len(new_image) // 1024

	new_image = rapi.imageDecodeRaw(new_image, width, height, "r5g5b5p1")

	tex1 = NoeTexture("Texture_0", width, height, new_image, noesis.NOESISTEX_RGBA32)
	texList.append(tex1)

	return 1


