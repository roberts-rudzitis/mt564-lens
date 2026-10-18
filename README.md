# MT564 Lens

A Python tool that generates synthetic SWIFT MT564 corporate action messages for testing and learning.

All data is fake: invented company names, randomly built ISINs with valid check digits, and placeholder BIC codes. No real client or bank data is used.

## Who is this for?

**Developers building banking or custody systems.** Real MT564 messages contain confidential client data and can't be shared for testing. Synthetic messages can feed test environments, check how a parser handles edge cases, or train new staff on the message structure without exposing anyone's information.

**Students and trainees.** Learning SWIFT formats from documentation alone is slow. Generating a batch of messages and comparing them shows the tags, date sequence, and rate formatting in practice.

**Operations and compliance teams.** The `--seed` option makes every run reproducible, so a test scenario can be recreated exactly for troubleshooting or audit.

**The open-source community.** Public examples of financial messaging formats are rare because real samples are protected. This project aims to fill that gap for anyone searching for MT564 examples or SWIFT test data.

## Status

Version 0.1 supports cash dividend events only (`CAEV//DVCA`, message function `NEWM`).

## Example output

```
{1:F01TESTBEBBAXXX0000000000}{2:I564TESTDEFFXXXXN}{4:
:16R:GENL
:20C::SEME//MSG00001
:23G:NEWM
:22F::CAEV//DVCA
:98A::PREP//20260308
:20C::CORP//CA00000001
...
:98A::EXDT//20260310
:98A::RDTE//20260313
:98A::PAYD//20260412
:92A::GRSS//3,84
...
-}
```

## Requirements

- Python 3.10 or newer
- pytest (installed from `requirements.txt`)

## Setup

Windows (PowerShell):

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Mac/Linux:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the tests

```
python -m pytest
```

The tests check message count, mandatory tags, date order, ISIN check digits, and that the same seed always produces the same output.

## Generate sample messages

Windows (PowerShell):

```
$env:PYTHONPATH="src"; python -m mt564lens.generator --count 20 --seed 1 --output sample_data/
```

Mac/Linux:

```
PYTHONPATH=src python -m mt564lens.generator --count 20 --seed 1 --output sample_data/
```

| Option     | Default       | Description                          |
|------------|---------------|--------------------------------------|
| `--count`  | `10`          | Number of messages to generate       |
| `--seed`   | `42`          | Random seed; same seed, same output  |
| `--output` | `sample_data` | Folder where `.txt` files are saved  |

Each message is saved as `mt564_0001.txt`, `mt564_0002.txt`, and so on.

## Project layout

```
src/mt564lens/generator.py   Message generator and command-line tool
tests/test_generator.py      Pytest test suite
sample_data/                 Generated sample messages
pytest.ini                   Pytest settings
requirements.txt             Python dependencies
```

## Roadmap

- Additional corporate action event types
- Parsing and validation of generated MT564 messages

## License

See [LICENSE](LICENSE).