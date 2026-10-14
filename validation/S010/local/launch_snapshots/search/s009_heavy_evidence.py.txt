"""Read effective heavy source without rewriting historical attempt outcomes."""
import json
from pathlib import Path

def effective_heavy():
    root=Path('validation/S009')
    extension=root/'heavy_extended/result.json'
    if extension.exists():
        row=json.loads(extension.read_text())
        if row['verdict']=='NON_BIPLANAR_DRAT_VERIFIED':return row,extension,root/'heavy_extended/search/K7-I5'
    record=root/'heavy/result.json'
    return json.loads(record.read_text()),record,root/'heavy/search/K7-I5'
