import utils

examples = [
    "Rajakalakshmi Engineering College",
    "Rajakalashmi engineering college",
    "rmk",
    "RMK",
    "Rmk",
    "R.M.K",
    "R.m.k"
]

print("Original -> Normalized")
print("-" * 30)
for ex in examples:
    norm = utils.normalize_college_name(ex)
    print(f"'{ex}' -> '{norm}'")
