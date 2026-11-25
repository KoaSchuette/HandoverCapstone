# Command Parser: Development Log

Progress record for the local-SLM command parser (final stage voice pipeline). It covers the design decisions, each test run, why failures happened, and what was changed in response.

Date of record: 2026-11-24. Timing figures cover the parser only (not VAD or Whisper). The final prompt is in `command_parser.py` in the repository, which is the most current version.

Requirement links: R1 (delivery and return in 15 s or less, target 5 s) and R5 (correct tool in at least 96% of attempts).

---

## 1. Goal

Take the transcript of a spoken command (for example "Pass me the green screwdriver") and produce a structured command: a **function** and a **subject**, which are then converted to numeric codes for the robot.

| Functions | Subjects |
|---|---|
| unknown, deactivate_voice, reactivate_voice, deliver_tool, cancel_task, pause_task, resume_task | none, red_screwdriver, green_screwdriver, blue_screwdriver |

Additional Notes:
- Deactivating puts the system in a state where it ignores task commands until voice is reactivated.
- A delivery request that does not name a colour ("needs clarification") is treated the same as `unknown` for now.

## 2. Design decisions

| Decision | Choice | Reasoning |
|---|---|---|
| What the LLM outputs | Names (`"deliver_tool"`), not numbers | The numeric codes live in a plain dictionary (`commands.py`), so they can be read, tested and changed without adjusting the model. |
| Cloud vs local model | Local (Ollama, `qwen2.5:3b`) | Parsing takes about 0.4 to 0.6 s locally, which is comparable to a cloud call. It works offline, needs no API key and costs nothing per call |
| Output format | JSON forced to a schema with enum lists | The model can only choose names from the vocabulary. Easier to validate than free text |
| Randomness | `temperature = 0` | The same input gives the same output, so tests are repeatable |
| Latency | `keep_alive` and a warm-up call at startup | The first call loads the model (several seconds). Later calls are faster matching the 0.4-0.6s metric. |
| Where logic lives | Validation and voice on/off state in `controller.py`, not the LLM | Safety-relevant rules should be deterministic code, not model behaviour. This also includes forseeable errors that can be avoided outside of the SLM. |

## 3. Files

| File | Function |
|---|---|
| `commands.py` | Vocabulary (`FUNCTION_CODES`, `SUBJECT_CODES`) and `normalise()` for known speech-recognition mistakes |
| `command_parser.py` | Talks to the LLM. `parse_command(text)` returns `(command_dict, seconds)` |
| `controller.py` | `validate()` cleans the model output. `Controller` holds the voice on/off state and converts names to codes |
| `test_cases.py` | The test phrases, grouped by category, each with the expected result |
| `test_parser.py` | Runs every case; reports accuracy by category, failures by severity, and timing |

## 4. Timeline of results

Test sets differ between rows 1 to 2 (16 cases) and 3 to 5 (80 cases), so the accuracy percentages are not directly comparable.

| # | Test set | Change made before the run | Accuracy | Tool errors | Mean / max time |
|---|---|---|---|---|---|
| 1 | 16 cases | Initial build | 14/16 (88%) | 1 | 0.46 s / 0.62 s |
| 2 | 16 cases | Prompt rules; "read" to "red" fix; resume, pause and reactivate examples | 15/16 (94%) | 1 | 0.43 s / 0.48 s |
| 3 | 80 cases | None (set enlarged and categorised) | 68/80 (85%) | 7 | 0.43 s / 0.58 s |
| 4 | 80 cases | Colour guard; non-overlapping function descriptions; "instructions only" rule | 73/80 (91%) | 0 | 0.44 s / 0.57 s |
| 5 | 80 cases | More resume, reactivate and negative examples | 78/80 (98%) | 0 | 0.43 s / 0.57 s |

"Tool errors" means a delivery when none was requested, or delivery of the wrong colour.

### Run 1: initial build (14/16)
Failures:
- `pass me a screwdriver` returned `deliver_tool, red_screwdriver`. The model guessed a colour that was never spoken.
- `okay continue` returned `unknown` instead of `resume_task`.

### Run 2: first prompt changes (15/16)
Changes:
- Stated explicitly that "read" means red, and added a "never guess a colour" rule.
- Added examples for resume, pause and reactivate (the prompt had none).
- Added `normalise()` in code so "read" becomes "red" before the model sees the text.

Result: `okay continue` and the "read" case passed. `pass me a screwdriver` still returned red.

### Run 3: larger test set (68/80)
The set was extended to 80 cases in 10 categories (delivery, no colour, unsupported colour, two colours, deactivate, reactivate, cancel, pause, resume, off-topic), and the test script now classifies each failure: false delivery, wrong tool, wrong command, or missed.

| Category | Result |
|---|---|
| deliver | 19/19 |
| no_colour | 9/14 |
| bad_colour | 6/6 |
| multi_colour | 1/2 |
| deactivate / reactivate | 6/6 and 6/6 |
| cancel | 5/6 |
| pause | 5/5 |
| resume | 3/6 |
| off_topic | 8/10 |

Failures:
- **7 tool errors:** five no-colour requests all returned red; `give me the red or green screwdriver` returned red; `that is a nice green screwdriver` delivered green.
- **Wrong commands:** `stop the delivery` became deactivate_voice; `okay go on` became reactivate_voice; `I dropped the red screwdriver` became cancel_task.
- **Missed:** `keep going`, `proceed`.

### Run 4: colour guard and clearer definitions (73/80)
Changes:
- **Colour guard in `controller.py`:** a delivery is accepted only if exactly one tool colour appears in the transcript and it matches the model's choice. Otherwise the command becomes `unknown`. `validate` and `handle` now take the transcript text as well.
- Rewrote the function descriptions so they do not overlap (deactivate and reactivate apply only when voice or listening is mentioned).
- Added a rule that only instructions to the robot are commands; comments and questions are `unknown`.

Result: all tool errors removed. Remaining failures: `hand me that` returned pause_task, `I dropped the red screwdriver` returned cancel_task, `listen again` was missed, and four resume phrases were missed (`continue please`, `keep going`, `okay go on`, `proceed`).

### Run 5: more examples (78/80)
Changes: added more resume and reactivate examples with varied wording, and negative examples (statements such as an object falling, and "give me those").

Remaining failures:
- `I dropped the red screwdriver` returned `cancel_task` (wrong command).
- `keep going` returned `unknown` (missed).

## 5. Why the failures happened

| Failure | Cause | What fixed it |
|---|---|---|
| Colour guessed when none spoken | The 3B model falls back to the first colour (red) when unsure. Prompt wording alone reduced but did not remove it | A deterministic guard in code that checks the colour was actually spoken |
| "read" not understood as red | Speech recognition produces homophones; the model treated "read" as not a colour | `normalise()` in code, plus an explicit prompt rule |
| Two colours spoken | The model picks one of them | The guard requires exactly one spoken colour |
| Statement treated as a request | The model matched the words (screwdriver, colour) without checking intent | An "instructions only" rule and negative examples |
| stop / go on mapped to the wrong command | Function descriptions overlapped ("stop" could mean cancel or stop listening) | Rewritten descriptions with distinct triggers |
| Resume phrases missed | Few resume examples, and the new "instructions only" rule made the model more cautious | More diverse resume examples |

Observations:
- A 3B model learns more from several varied examples than from written descriptions.
- Stricter rules reduce one kind of error but can make the model over-cautious (more `unknown`).
- Wrong cancel or pause commands are more serious than a missed command, because a wrong command could interrupt a delivery, while a miss only means the operator repeats it. Code cannot guard these as simply as it does for colour.

## 6. Limits of these results

- **The 80 cases are a tuning set.** The prompt was adjusted after seeing its failures, so the 98% is optimistic and is not a measure of unseen performance.
- **Sample size.** 78/80 is consistent with a true accuracy somewhere between about 91% and 99%, so it cannot show the 96% threshold on its own.
- **R5 is end-to-end.** It includes Whisper, so parser accuracy and transcription accuracy combine. A misheard colour is turned into `unknown` by the guard (a safe failure, but still not a delivery).
- **Rough sizing for evidence.** With zero tool errors in n fresh trials, the 95% upper bound on the error rate is about 3/n, so roughly 75 fresh delivery-related cases with no tool errors are needed to show a rate under 4%, and more if any occur.

## 7. Known limitations (current)

- `I dropped the red screwdriver` is interpreted as `cancel_task`.
- Some resume phrasings (e.g. `keep going`) are missed.
- A delivery without a colour, or with two colours, is `unknown` (no clarification question yet).
- Tested only on typed text, not yet on real Whisper transcripts.

## 8. Next steps

1. Freeze the prompt and code (commit) so the final test is honest.
2. Evaluate on a fresh held-out set that was not used for tuning.
3. Evaluate on real Whisper transcripts from recorded clips, then run the full end-to-end test (record, VAD, Whisper, parser) and count correct tools out of attempts.
4. Compare models for stage 05 (for example `qwen2.5:7b` and `llama3.2:3b`): accuracy, tool errors, mean and max time.
5. Update `README_command_parser.md` with the guard, `handle(cmd, text)` and the latest results.
