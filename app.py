import os
import sys
import subprocess
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory

import torch
from modelscope import AutoModelForCausalLM, AutoTokenizer
from modelscope import GenerationConfig
import threading

app = Flask(__name__)

# # 启动 FastAPI 服务的函数
# def start_fastapi():
#     subprocess.run([sys.executable, 'server_wss.py'])
#
# # 在 Flask 应用启动时启动 FastAPI 服务
# @app.before_request
# def launch_fastapi():
#     # 在独立线程中启动 FastAPI 服务
#     threading.Thread(target=start_fastapi).start()

fastapi_started = False  # 用于标记 FastAPI 是否已启动

# 启动 FastAPI 服务的函数
def start_fastapi():
    subprocess.run([sys.executable, 'server_wss.py'])

# 在 Flask 启动时，检查 FastAPI 是否已启动
@app.before_request
def launch_fastapi():
    global fastapi_started
    if not fastapi_started:
        threading.Thread(target=start_fastapi).start()
        fastapi_started = True


OUTPUT_FOLDER = 'outputs'

# 确保 outputs 目录存在
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


@app.route('/save_text', methods=['POST'])
def save_text():
    data = request.json
    text = data.get('text', '')

    # 生成带时间戳的文件名（避免覆盖）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"transcription_{timestamp}.txt"
    filepath = os.path.join(OUTPUT_FOLDER, filename)

    # 写入文件
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)
        return jsonify({
            'status': 'success',
            'filepath': filepath
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# Directory to store the uploaded audio files
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
OUTPUT_FOLDER = os.path.join(os.getcwd(), 'outputs')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)


def read_from_txt(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()
    return content


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/save', methods=['POST'])
def save_audio():
    if 'audio_data' not in request.files:
        return jsonify({"message": "未上传录音文件"}), 400

    audio_file = request.files['audio_data']
    # Generate a unique filename using timestamp and save in the original format (.webm)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}.webm"
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    # Save the uploaded audio file as is (no conversion)
    audio_file.save(file_path)

    # Convert the .webm file to .mp3
    mp3_file_path = convert_webm_to_mp3(file_path, OUTPUT_FOLDER)

    # Run the model on the converted .mp3 file
    txt_file_path = run_model_on_mp3(mp3_file_path, OUTPUT_FOLDER)

    return jsonify({"message": "保存成功并转换为MP3", "filename": filename, "txt_file": txt_file_path}), 200


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/outputs/<filename>')
def output_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)


@app.route('/read')
def read_audio():
    try:
        # Set environment variables to force UTF-8 encoding
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["LANG"] = "zh_CN.UTF-8"

        result = subprocess.run(
            [sys.executable, "read_txt.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True,
            env=env
        )
        output = result.stdout.strip()
        return jsonify({"message": output}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({"message": "读取失败", "error": e.stderr.strip()}), 500

#释放模型，每次都重新加载
# @app.route('/generate', methods=['POST'])
# def generate():
#     try:
#         input_path = request.json.get('path')
#         text1 = read_from_txt(input_path)
#         print("text1",text1)
#         x1 = '这是我的超声检查报告单，请根据超声检查报告单作出诊断'
#         x2 = ("请根据医生和超声机器输出给出初步诊断，只需要一个总结性的诊断结果。")
#         x3 = ("患者的甲状腺右叶大小为4.5x2.0x1.8厘米，左叶大小为4.3x2.1x1.7厘米。"
#               "在右侧甲状腺的中部发现了一个低回声结节，大小约为0.8x0.6厘米，边界清晰，形状规则，内部有点状强回声。"
#               "此外，这个结节还显示了血液供应信号。至于颈部淋巴结，双侧均未发现明显异常肿大。")
#
#         text = x1 +x2 +"医生诊断:"+ text1 +"。超声机器输出："+x3
#
#         # Clear cache before generating
#         torch.cuda.empty_cache()
#
#         # Load model and tokenizer
#         tokenizer = AutoTokenizer.from_pretrained('./model/Q-7', trust_remote_code=True)
#         model = AutoModelForCausalLM.from_pretrained('./model/Q-7', device_map="auto", trust_remote_code=True,
#                                                      fp16=True).eval()
#         model.generation_config = GenerationConfig.from_pretrained('./model/Q-7', trust_remote_code=True)
#
#         response, _ = model.chat(tokenizer, text, history=None)
#
#         # Release model and tokenizer
#         del model
#         del tokenizer
#         torch.cuda.empty_cache()
#
#         return jsonify({"response": response}), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

#模型一直处于加载状态
# 全局变量，用于存储模型和分词器
model = None
tokenizer = None
model_loaded = False  # 标记模型是否已加载

# 在应用启动时加载模型
@app.before_request
def load_model():
    global model, tokenizer, model_loaded
    if not model_loaded:  # 确保模型只加载一次
        try:
            print("Loading model and tokenizer...")
            # 加载模型和分词器
            tokenizer = AutoTokenizer.from_pretrained('./model/Q-7', trust_remote_code=True)
            model = AutoModelForCausalLM.from_pretrained('./model/Q-7', device_map="auto", trust_remote_code=True,
                                                        fp16=True).eval()
            model.generation_config = GenerationConfig.from_pretrained('./model/Q-7', trust_remote_code=True)
            model_loaded = True
            print("Model and tokenizer loaded successfully.")
        except Exception as e:
            print(f"Error loading model: {e}")

# 清理 GPU 缓存函数
def clear_cuda_cache():
    torch.cuda.empty_cache()

@app.route('/generate', methods=['POST'])
def generate():
    try:
        input_path = request.json.get('path')
        text1 = read_from_txt(input_path)  # 假设你有这个函数
        print("text1", text1)

        x1 = '这是我的超声检查报告单，请根据超声检查报告单作出诊断'
        x2 = ("请根据医生和超声机器输出给出初步诊断，只需要一个总结性的诊断结果。")
        x3 = ("患者的甲状腺右叶大小为4.5x2.0x1.8厘米，左叶大小为4.3x2.1x1.7厘米。"
              "在右侧甲状腺的中部发现了一个低回声结节，大小约为0.8x0.6厘米，边界清晰，形状规则，内部有点状强回声。"
              "此外，这个结节还显示了血液供应信号。至于颈部淋巴结，双侧均未发现明显异常肿大。")

        text = x1 + x2 + "医生诊断:" + text1 + "。超声机器输出：" + x3

        # 清理 GPU 缓存
        clear_cuda_cache()

        # 使用已加载的模型和分词器生成响应
        response, _ = model.chat(tokenizer, text, history=None)

        return jsonify({"response": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/report')
def report():
    return render_template('report.html')

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

    return mp3_file_path


def run_model_on_mp3(mp3_file_path, output_folder):
    """
    Run the model on the converted .mp3 file and save the output to a .txt file.
    """
    from funasr import AutoModel
    from funasr.utils.postprocess_utils import rich_transcription_postprocess

    def save_to_txt(filename, content):
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"内容已保存到 {filename}")

    # model_dir = "/home/se/.cache/modelscope/hub/iic/SenseVoiceSmall"
    # model = AutoModel(
    #     model=model_dir,
    #     trust_remote_code=True,
    #     remote_code="./model.py",
    #     vad_model="fsmn-vad",
    #     vad_kwargs={"max_single_segment_time": 30000},
    #     device="cuda:0",
    # )
    # 在app.py中添加本地模型路径配置
    model_config = {
        "model": "model/SenseVoiceSmall",
        "vad_model": "model/speech_fsmn_vad_zh-cn-16k-common-pytorch",
        "local_files_only": True,
        "device": "cuda:0" if torch.cuda.is_available() else "cpu"
    }

    # 修改模型加载方式
    model = AutoModel(
        model=model_config["model"],
        vad_model=model_config["vad_model"],
        local_files_only=model_config["local_files_only"],
        device=model_config["device"]
    )
    res = model.generate(
        input=mp3_file_path,
        cache={},
        language="auto",  # "zh", "en", "yue", "ja", "ko", "nospeech"
        use_itn=True,
        batch_size_s=60,
        merge_vad=True,  #
        merge_length_s=15,
    )
    text = rich_transcription_postprocess(res[0]["text"])

    # Save the transcription to a .txt file
    base_name = os.path.splitext(os.path.basename(mp3_file_path))[0]
    txt_file_path = os.path.join(output_folder, f"{base_name}.txt")
    save_to_txt(txt_file_path, text)

    return txt_file_path

@app.route('/submit-ultrasound-findings', methods=['POST'])
def submit_ultrasound_findings():
    data = request.get_json()
    data = str(data)
    # 在这里处理接收到的数据
    print(data)
    x1 = '这是我的超声检查报告单，'
    x2 = ('请根据超声检查报告单作出诊断')
    x3 = ("患者的甲状腺右叶大小为4.5x2.0x1.8厘米，左叶大小为4.3x2.1x1.7厘米。在右侧甲状腺的中部发现了一个低回声结节，大小约为0.8x0.6厘米，边界清晰，形状规则，内部有点状强回声。此外，这个结节还显示了血液供应信号。至于颈部淋巴结，双侧均未发现明显异常肿大。")
    text = x1 + data + x2 +x3
   # Clear cache before generating
    torch.cuda.empty_cache()

    # Load model and tokenizer
    tokenizer = AutoTokenizer.from_pretrained('/home/se/Qwen/Q-7', trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained('/home/se/Qwen/Q-7', device_map="auto", trust_remote_code=True,
                                                 fp16=True).eval()
    model.generation_config = GenerationConfig.from_pretrained('/home/se/Qwen/Q-7', trust_remote_code=True)

    response, _ = model.chat(tokenizer, text, history=None)
    print(response)

    # Release model and tokenizer
    del model
    del tokenizer
    torch.cuda.empty_cache()
    return jsonify({"success": response}), 200
#     return jsonify({'success': True})


if __name__ == '__main__':
    app.run(debug=True)