# ================================================================================
# Rayman Revolution (PS2)
# Extract DSC / BF archives
# Python script by DKDave, 2024
# ================================================================================


import os, sys, struct


print("--------------------------------------------------------------------------------")
print("Rayman Revolution (PS2)")
print("DSC / BF extract")
print("Python script by DKDave, 2024\n")
print("Usage:\tpython dsc.py [dsc file name] [output folder]")
print("--------------------------------------------------------------------------------\n")

if len(sys.argv) != 3:
	print("Not enough arguments provided.  Please try again.")
	exit()

out_folder = sys.argv[2]

os.makedirs(out_folder, 0o777, True)

dsc_file = sys.argv[1]
bf_file = dsc_file.replace(".dsc", ".bf")

f = open(dsc_file, "rb")
f2 = open(bf_file, "rb")

list = bytearray(f.read())
files = []
num = 0

f.seek(5)

info = ""

while True:
	temp = int.from_bytes(f.read(1), "little")

	if temp == 0x29:
		break

	if temp == 0x5d:
		files.append(info.split(","))
		info = ""
		num += 1

	elif temp != 0x5b:
		info += chr(temp)

for info in files:
	filename = info[0]
	offset = int(info[1])
	size = int(info[2])
	misc = int(info[3])

	print(f"{'Writing ... ' + filename:<30}")

	f2.seek(offset)
	data = f2.read(size)

	out = open(out_folder + "\\" + filename, "wb")
	out.write(data)
	out.close()

f.close()
f2.close()


