import sys
import os
from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess


def save_to_txt(filename, content):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"内容已保存到 {filename}")


def process_mp3(mp3_file_path, output_folder):
    model_dir = "iic/SenseVoiceSmall"
    model = AutoModel(
        model=model_dir,
        trust_remote_code=True,
        remote_code="./model.py",
        vad_model="fsmn-vad",
        vad_kwargs={"max_single_segment_time": 30000},
        device="cuda:0",
    )

    res = model.generate(
        input=mp3_file_path,
        cache={},
        language="auto",  # "zh", "en", "yue", "ja", "ko", "nospeech"
        use_itn=True,
        batch_size_s=60,
        merge_vad=True,
        merge_length_s=15,
    )
    text = rich_transcription_postprocess(res[0]["text"])
    print(text)

    # Save the transcription to a .txt file
    base_name = os.path.splitext(os.path.basename(mp3_file_path))[0]
    txt_file_path = os.path.join(output_folder, f"{base_name}.txt")
    save_to_txt(txt_file_path, text)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: mp3_to_text.py <mp3_file_path> <output_folder>")
        sys.exit(1)

    mp3_file_path = sys.argv[1]
    output_folder = sys.argv[2]
    process_mp3(mp3_file_path, output_folder)