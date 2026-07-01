import scripts.verify_forecast_determinism as v
import json
import dataclasses

engine = v.build_engine()
history = v.create_mock_history()
fc1 = engine.build_forecast_context(history)
fc2 = engine.build_forecast_context(history)

d1 = dataclasses.asdict(fc1)
d2 = dataclasses.asdict(fc2)

def compare_dicts(d1, d2, path=""):
    if isinstance(d1, dict) and isinstance(d2, dict):
        for k in d1:
            if k not in d2:
                print(f"{path}.{k} missing in d2")
            else:
                compare_dicts(d1[k], d2[k], f"{path}.{k}")
        for k in d2:
            if k not in d1:
                print(f"{path}.{k} missing in d1")
    elif isinstance(d1, list) and isinstance(d2, list):
        for i, (v1, v2) in enumerate(zip(d1, d2)):
            compare_dicts(v1, v2, f"{path}[{i}]")
    else:
        if d1 != d2:
            print(f"{path} differs: {d1} != {d2}")

compare_dicts(d1, d2)
