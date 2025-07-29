def handle_txt(path, output_format="text"):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return content if output_format == "text" else {"text": content, "tables": []}
