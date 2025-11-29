import json

input_file = "/home/me/Downloads/fine_tuning_llm/banking77_subset_training.jsonl"
output_file = "/home/me/Downloads/fine_tuning_llm/banking77_fixed.jsonl"

with open(input_file, "r", encoding="utf-8") as fin, \
     open(output_file, "w", encoding="utf-8") as fout:

    for line in fin:
        line = line.strip()
        if not line:
            continue

        obj = json.loads(line)

        instruction = obj.get("instruction", "").strip()
        inp = obj.get("input", "").strip()
        out = obj.get("output", "").strip()

        # Build text exactly like the working Vertex example
        user_text = f"{instruction}\n\n{inp}"

        vertex_obj = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": user_text}
                    ]
                },
                {
                    "role": "model",
                    "parts": [
                        {"text": out}
                    ]
                }
            ]
        }

        fout.write(json.dumps(vertex_obj, ensure_ascii=False) + "\n")

print("DONE. File written to:", output_file)