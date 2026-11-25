# Lottery Probability Engine

[![CI](https://github.com/AhmadEblagh205/lottery-probability-app/actions/workflows/ci.yml/badge.svg)](https://github.com/AhmadEblagh205/lottery-probability-app/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

This is an educational probability engine for an illustrative uniform 6-from-49 lottery. I started it as a guided Dataquest lottery-addiction-awareness project and then rebuilt it on my own as a combinatorics exercise. The prize table is illustrative, so the results do not describe any real operator.

## What it does

- Counts the exact match probabilities for a 6-from-49 draw.
- Separates holding N distinct tickets in one draw from buying one ticket in each of N independent draws.
- Computes expected value for a fixed illustrative prize table and simulates finite-horizon outcomes.
- Checks a ticket against a historical draw file, with strict validation of the input.
- Reports the calculations from a command line interface.

## Results

There are 13,983,816 unordered six-number tickets, so one ticket has a jackpot probability of 1 in 13,983,816. Every valid combination has the same probability, including `1-2-3-4-5-6`.

With N distinct tickets in one draw the jackpot probability is N / 13,983,816. With one ticket in each of N independent draws it is 1 - (1 - p)^N. At N = 13,983,816 the first case gives 100% coverage and the second gives about 63.2%.

The illustrative prizes are £5m for six matches, £1,750 for five, £140 for four and £30 for three. A £2 ticket then has expected winnings of £1.055 and an expected loss of £0.945, which is 47.25% of the ticket price.

Over 200,000 independent plays under this model the expected number of jackpots is 0.0143 and the chance of none is 98.58%. Conditional on no jackpot, the expected loss is about £1.303 per play. The expected value does not change with the horizon. The payout is heavily skewed, so a typical outcome sits well away from the mean.

## How to run

```bash
pip install -r requirements.txt

python src/cli.py --tickets 100
python src/cli.py --plays 200000
python src/cli.py --ev --ticket-price 2
python src/cli.py --simulate 200000 --worlds 10000
python src/audit.py

# Optional historical check, with a Kaggle-format file at data/raw/649.csv
python src/cli.py --ticket 3 12 19 27 33 41 --check-history

pytest -q
```

The first version had 5 tests and the current one has 20. They cover the exact match partition, the two meanings of N tickets, the expected-value reconstruction, the finite-horizon identities, simulation sanity, domain errors and ticket and history validation.

## Notes

The historical file is optional and is not included. The loader checks the six draw columns, integer values, the 1 to 49 range and distinctness within a draw. Under the independent uniform model a past frequency does not change the next draw probability. I do not model shared jackpots or how popular a number is with players. Assumptions and claim boundaries are in `docs/METHODOLOGY.md`.

## Licence

MIT, see [LICENSE](LICENSE).
