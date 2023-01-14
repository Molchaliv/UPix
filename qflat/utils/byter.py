import os


def chunks(data: str, splitter: int = 5):
	for index in range(0, len(data), splitter):
		yield data[index:index + splitter]


def create_bytes_res(folder: str, output: str = "output_res.py"):
	folder = folder.replace("/", "\\")
	output_data = ""
	if os.path.exists(folder) and os.path.isdir(folder):
		for filename in os.listdir(folder):
			if os.path.isfile(f"{folder}\\{filename}"):
				chunk_data = f"{filename.split('.')[0]} = "

				with open(f"{folder}\\{filename}", mode="rb") as file_bytes:
					chunk_data += str(file_bytes.read())

				output_data += f"{chunk_data}\n\n"

		with open(output, mode="w", encoding="utf-8") as output_file:
			output_file.write(output_data[:-1])
