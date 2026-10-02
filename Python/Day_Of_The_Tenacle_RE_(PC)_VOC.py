# ----------------------------------------------------------------------------------------------------
# Day Of The Tentacle (Remastered) (PC, 2016)
# VOC audio extractor
# Python script by DKDave, 2026
# ----------------------------------------------------------------------------------------------------

# Place this script in the same folder as the "tenta.cle" archive
# Audio files will be converted to playable .wav files and saved in "Output" folder

# Usage: [script name].py - no additional parameters required


import os, sys, struct


print("=" * 120)
print("Day Of The Tentacle (Remastered) - Dialogue/SFX extractor")
print("Python script by DKDave, 2026")
print("=" * 120 + "\n")

if not os.path.exists("tenta.cle"):
	print("Archive tenta.cle not found in this folder.  Please retry.")
	exit()

cle = open("tenta.cle", "rb")									# Main data archive

entry = 0x2f8cb										# VOC audio table
data_offset = 0x5fde53ed									# VOC data archive

codecs = {0: "PCM8 Unsigned"}								# Only PCM8_U in this game

out_folder = "Output"
os.makedirs(out_folder, 0o777, True)

print("-" * 120)
print(f"{'Filename':<40}{'Audio size':<20}{'Codec':<20}{'Samp rate':<15}")
print("-" * 120 + "\n")

while True:
	cle.seek(entry)
	offset = int.from_bytes(cle.read(4), "little")

	if offset == 0xffffffff:									# No more entries
		break

	else:
		filename = cle.read(0x40).decode("ascii").replace("\x00", "")
		aud_type = int.from_bytes(cle.read(4), "little")					# 0 = dialogue, 1 = SFX

		audio_data = bytearray()							# new audio data

		cle.seek(data_offset + offset + 4)
		vctl_size = int.from_bytes(cle.read(4), "big")
		offset += vctl_size + 0x1a

		while True:								# loop through VOC chunks until EOF marker
			cle.seek(data_offset + offset)
			chunk_type = int.from_bytes(cle.read(1), "little")

			if chunk_type == 0:							# EOF marker
				break

			elif chunk_type == 1:						# Audio data chunk
				chunk_size = int.from_bytes(cle.read(3), "little")
				rate = 1000000 // (256 - int.from_bytes(cle.read(1), "little"))
				codec = int.from_bytes(cle.read(1), "little")			# Always PCM8_U
				audio_data += cle.read(chunk_size - 2)

			offset += chunk_size + 4

		wav_header = struct.pack("<4sI8sIHHIIHH4sI", b"RIFF", len(audio_data) + 0x24, b"WAVEfmt ", 0x10, 1, 1, rate, rate, 1, 8, b"data", len(audio_data))

		out_file = out_folder + "\\" + filename + ".wav"

		if len(audio_data) > 0:

			if not os.path.exists(out_file):
				print(f"{filename:<40}{str(len(audio_data)) + ' bytes':<20}{codecs[codec]:<20}{str(rate) + ' Hz':<15}")

				zzz = open(out_file, "wb")
				zzz.write(wav_header + audio_data)
				zzz.close()

			else:
				print(f"{filename:<40}{str(len(audio_data)) + ' bytes':<20}{codecs[codec]:<20}{str(rate) + ' Hz':<15}{'File already exists':<20}")

	entry += 0x48

cle.close()

