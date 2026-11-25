from collections import defaultdict

from command_parser import parse_command
from controller import validate
from test_cases import CASES


def failure_kind(got, expected):
    if got[0] == "deliver_tool" and expected[0] != "deliver_tool":
        return "FALSE DELIVERY"        # delivered when it shouldn't have
    if got[0] == "deliver_tool":
        return "WRONG TOOL"            # delivered, but the wrong colour
    if got[0] == "unknown":
        return "MISSED"                # understood nothing; operator repeats it
    return "WRONG COMMAND"             # a different command than expected


parse_command("warm up")   # first call loads the model; don't time it

by_category = defaultdict(lambda: [0, 0])    # category -> [passed, total]
times = []
failures = []

for category, text, exp_f, exp_s in CASES:
    cmd, secs = parse_command(text)
    got = validate(cmd, text)
    expected = (exp_f, exp_s)
    ok = got == expected

    by_category[category][1] += 1
    by_category[category][0] += ok
    times.append(secs)
    if not ok:
        failures.append((failure_kind(got, expected), category, text, got, expected))

print("\n--- By category ---")
for category, (passed, total) in by_category.items():
    print(f"{category:13s} {passed}/{total}")

print("\n--- Failures (tool errors first) ---")
order = {"FALSE DELIVERY": 0, "WRONG TOOL": 1, "WRONG COMMAND": 2, "MISSED": 3}
for kind, category, text, got, expected in sorted(failures, key=lambda f: order[f[0]]):
    print(f"{kind:14s} [{category}] {text!r} -> {got} (expected {expected})")

total = len(CASES)
passed = total - len(failures)
tool_errors = sum(1 for f in failures if f[0] in ("FALSE DELIVERY", "WRONG TOOL"))
print(f"\nAccuracy: {passed}/{total} = {100 * passed / total:.0f}%")
print(f"Tool errors (false delivery + wrong tool): {tool_errors}")
print(f"Time: mean {sum(times) / len(times):.2f}s, max {max(times):.2f}s")