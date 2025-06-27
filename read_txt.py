import sys
import io
import os

# Ensure standard output uses UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Define the output folder
output_folder = "outputs"

if not os.path.exists(output_folder):
    print("没有读取到内容")
    sys.exit(1)

# Get all .txt files
txt_files = [f for f in os.listdir(output_folder) if f.endswith(".txt")]
if not txt_files:
    print("没有读取到内容")
    sys.exit(1)

# Sort by modification time and get the latest file
txt_files.sort(key=lambda x: os.path.getmtime(os.path.join(output_folder, x)))
latest_file = os.path.join(output_folder, txt_files[-1])

# Read the latest .txt file content
with open(latest_file, "r", encoding="utf-8") as f:
    content = f.read()

# Output the content or a message if empty
if content:
    print(content)
else:
    print("无内容")