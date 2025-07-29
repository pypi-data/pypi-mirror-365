import pandas as pd

def handle_xlsx(path, output_format="text"):
    xls = pd.ExcelFile(path)
    all_text = []
    all_tables = []

    for sheet_name in xls.sheet_names:
        df = xls.parse(sheet_name)
        text = df.to_string(index=False)
        all_text.append(f"Sheet: {sheet_name}\n{text}")
        all_tables.append({
            "sheet": sheet_name,
            "data": df.fillna("").values.tolist()
        })

    return "\n\n".join(all_text) if output_format == "text" else {
        "text": "\n\n".join(all_text),
        "tables": all_tables
    }
