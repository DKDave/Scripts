# ================================================================================
# Colony Wars (PS1)
# Extract voices and music from INF/PAK files
# Python script by DKDave, 2024
# ================================================================================

# Use with DATABASE.INF/DATABASE.PAK and MISSIONS.INF/MISSIONS.PAK - INF files can be extracted from the GAME.RSC archive
# Audio is extracted as raw .XA files which can be played in Foobar/vgmstream


import os, struct, sys


# Read XA sectors for a specific file

def get_xa(pak, start_sector, file_id, sector_count):
	xa_data = bytearray(sector_count * 0x930)
	offset = start_sector * 0x930
	xa_off = 0
	pak_len = os.stat(sys.argv[2])[6]

# read until all sectors are found for this file

	while True:
		pak.seek(offset + 0x11)
		sector_id = int.from_bytes(pak.read(1), "little")

		if sector_id == file_id:
			pak.seek(offset)
			xa_data[xa_off:xa_off + 0x930] = pak.read(0x930)
			sector_count -= 1
			xa_off += 0x930

		offset += 0x930

		if sector_count == 0 or offset == pak_len:
			break

	return xa_data


print("================================================================================")
print("Colony Wars (PS1) - INF/PAK audio extract")
print("Python script by DKDave, 2024")
print("================================================================================\n")

if len(sys.argv) != 3:
	print("Incorrect number of parameters.  Please use: Python " + sys.argv[0] + " [inf file] [pak file]")
	exit()

inf = open(sys.argv[1], "rb")
pak = open(sys.argv[2], "rb")

inf.seek(0)
check = inf.read(4)

if check != b'STDT':
	print("Not a valid INF file.")
	inf.close()
	pak.close()
	exit()


# Read file table

inf.seek(4)
files = int.from_bytes(inf.read(4), "little")
entry = 8
outfile = sys.argv[1].replace(".inf", "")

for a in range(files):
	inf.seek((a * 0x18) + 8)
	start_sector = int.from_bytes(inf.read(4), "little")
	misc1 = int.from_bytes(inf.read(4), "little")
	misc2 = int.from_bytes(inf.read(4), "little")
	file_id = int.from_bytes(inf.read(4), "little")
	sector_count = int.from_bytes(inf.read(4), "little")

	xa_data = get_xa(pak, start_sector, file_id, sector_count)
	print("Writing file: ", a, "\t", str(len(xa_data)) + " bytes")

	out = open(outfile + str(a) + ".xa", "wb")
	out.write(xa_data)
	out.close()

inf.close()
pak.close()

