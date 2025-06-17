import os
import json

def convert_json_to_txt(input_dir, output_dir, recursive=False):
    if not os.path.isdir(input_dir):
        print(f"Error: '{input_dir}' is not a valid directory.")
        return

    os.makedirs(output_dir, exist_ok=True)

    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.json'):
                input_path = os.path.join(root, file)

                # Build relative path for output (preserves subdir structure)
                rel_path = os.path.relpath(root, input_dir)
                output_subdir = os.path.join(output_dir, rel_path)
                os.makedirs(output_subdir, exist_ok=True)

                output_path = os.path.join(output_subdir, file.replace('.json', '.txt'))

                try:
                    with open(input_path, 'r', encoding='utf-8') as jf:
                        data = json.load(jf)

                    with open(output_path, 'w', encoding='utf-8') as tf:
                        json.dump(data, tf, indent=4)

                    print(f"Converted: {input_path} -> {output_path}")
                except Exception as e:
                    print(f"Failed to convert '{input_path}': {e}")

        if not recursive:
            break

# Hardcoded usage for your case
if __name__ == '__main__':
    input_dir = r'D:\Projects\open-ai-rag\docs'
    output_dir = os.path.join(os.path.dirname(input_dir), 'txt_docs')
    convert_json_to_txt(input_dir, output_dir, recursive=True)
