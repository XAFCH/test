import os
import subprocess

def convert_webm_to_mp3(webm_file_path, output_folder):
    if not os.path.exists(webm_file_path):
        raise FileNotFoundError(f"Input file {webm_file_path} does not exist.")

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    base_name = os.path.splitext(os.path.basename(webm_file_path))[0]
    mp3_file_path = os.path.join(output_folder, f"{base_name}.mp3")

    command = [
        "ffmpeg",
        "-i", webm_file_path,
        "-q:a", "0",
        "-map", "a",
        mp3_file_path
    ]

    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Successfully converted {webm_file_path} to {mp3_file_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred during conversion: {e.stderr.decode()}")
        raise

if __name__ == "__main__":
    input_webm = "./uploads/20250301171126.webm"  # 替换为你的输入文件路径
    output_dir = "./outputs"  # 替换为你的输出文件夹路径
    convert_webm_to_mp3(input_webm, output_dir)