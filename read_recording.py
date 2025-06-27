import sys
import io
import os
from datetime import datetime

# Ensure standard output uses UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Define the output text
output_text = "读取成功"

# Create a new folder named 'outputs' if it does not exist
output_folder = "outputs"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Generate a timestamp based filename and write the output in a .txt file
timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
output_file_path = os.path.join(output_folder, f"output_{timestamp_str}.txt")
with open(output_file_path, "w", encoding="utf-8") as file:
    file.write(output_text)

# Print the output text to standard output
print(output_text)