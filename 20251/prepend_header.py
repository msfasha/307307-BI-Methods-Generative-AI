import os

header = """# install streamlit transformers torch
# pip install streamlit transformers torch

"""

# List of files to skip
skip_files = ["prepend_header.py"]

# Walk through directories
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".py") and file not in skip_files:
            file_path = os.path.join(root, file)
            # Normalize path separators to avoid issues
            file_path = os.path.normpath(file_path)
            
            print(f"Processing {file_path}...")
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Check if header is already there
                # We check the first line to be safe
                if content.lstrip().startswith("# install streamlit transformers torch"):
                    print(f"Skipping {file_path}, header seems present.")
                    continue
                
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(header + content)
                print(f"Updated {file_path}")
                
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

print("Done.")
