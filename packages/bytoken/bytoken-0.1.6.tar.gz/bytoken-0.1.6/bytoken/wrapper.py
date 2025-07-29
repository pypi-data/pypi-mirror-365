# bytoken/wrapper.py

import json
import base64
from ._bytoken_core import _ByTokenBase

class ByToken(_ByTokenBase):
    def save(self, path: str):
        stoi_raw_bytes = self.get_stoi()
        merges_raw = self.get_merges()

        stoi_b64 = {base64.b64encode(k).decode('ascii'): v for k, v in stoi_raw_bytes.items()}
        merges_str_keys = {f"{k[0]},{k[1]}": v for k, v in merges_raw.items()}

        model_data = {"vocab_b64": stoi_b64, "merges": merges_str_keys}

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(model_data, f, indent=4)

    def from_file(self, path: str):
        with open(path, 'r', encoding='utf-8') as f:
            model_data = json.load(f)

        stoi_raw_bytes = {base64.b64decode(k): v for k, v in model_data["vocab_b64"].items()}
        merges_raw = {tuple(map(int, k.split(','))): v for k, v in model_data["merges"].items()}

        self.set_stoi(stoi_raw_bytes)
        self.set_merges(merges_raw)
        self.rebuild_internal_state()