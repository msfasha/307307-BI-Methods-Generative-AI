import google.generativeai as genai


import sys
print("Python version:", sys.version)
print("Executable path:", sys.executable)


genai.configure(api_key="YOUR_API_KEY_HERE")
models = genai.list_models()
for m in models:
    print(m.name, m.supported_generation_methods)


