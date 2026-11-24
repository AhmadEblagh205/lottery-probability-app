# Lottery Probability Engine

[![CI](https://github.com/AhmadEblagh205/lottery-probability-app/actions/workflows/ci.yml/badge.svg)](https://github.com/AhmadEblagh205/lottery-probability-app/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

An educational probability engine for an **illustrative uniform 6-from-49 lottery**, originally started as a guided Dataquest lottery-addiction-awareness project and rebuilt as an independent combinatorics/audit exercise.

The audited version focuses on a deceptively important question: **what exactly does a probability statement mean?** It separates distinct-ticket coverage in one draw from repeated play across independent draws, distinguishes expected value from a typical finite-horizon outcome, validates historical input strictly, and avoids treating an illustrative payout table as a real operator's current expected value.

## Exact 6-from-49 probabilities

There are

\[
\binom{49}{6}=13,983,816
\]

unordered six-number tickets.

For a fixed ticket, the exact number of draws matching exactly \(k\) numbers is

\[
\binom{6}{k}\binom{43}{6-k}.
\]

The jackpot probability for one ticket is therefore **1 in 13,983,816**. Under a uniform draw, `1-2-3-4-5-6` has exactly the same jackpot probability as every other valid combination.

The integer combinatorial counts are exact; floating-point values are used only to display their ratios and expected-value calculations.

## “N tickets” has two different meanings

This was the main audit correction.

### Distinct tickets in one draw

If you hold \(N\) different combinations for the **same draw**, the jackpot outcomes are mutually exclusive:

\[
P(\text{jackpot})=\frac{N}{13,983,816}.
\]

```bash
python src/cli.py --tickets 100
```

### Repeated independent play

If instead you buy one ticket in each of \(N\) independent draws:

\[
P(\ge1\text{ jackpot})=1-(1-p)^N.
\]

```bash
python src/cli.py --plays 200000
```

The distinction becomes stark at \(N=13,983,816\): owning every possible distinct ticket in one draw gives **100% jackpot-combination coverage**, whereas the same number of independent one-ticket plays gives only about **63.2%** chance of at least one jackpot.

## Illustrative expected value — and why “typical” is not another EV

```bash
python src/cli.py --ev --ticket-price 2
```

Using the repository's deliberately illustrative fixed prize table — £5m for six matches, £1,750 for five, £140 for four and £30 for three — a £2 ticket has:

- expected winnings: **£1.055**;
- expected loss: **£0.945**;
- expected loss fraction: **47.25% of ticket price**.

This is **not** a claim about the current expected value of Canadian Lotto 6/49 or any other real operator. Real games can have changing and shared jackpots, secondary/bonus games and different prize rules.

The old repository described a 200,000-ticket simulation as converging to an “experienced EV” around the no-jackpot loss. That language was wrong. The expectation does not change. Instead, the payout distribution is extremely skewed.

For **200,000 independent plays** under the toy model:

- expected jackpots: **0.0143**;
- probability of no jackpot: **98.58%**;
- unconditional expected loss: **£0.945/play**;
- expected loss conditional on no jackpot: **about £1.303/play**.

A 200,000-world Monte Carlo gives a median realised loss close to that no-jackpot value while the arithmetic mean is pulled toward the theoretical EV by the small number of jackpot worlds. That is a lesson about **mean versus typical finite-horizon outcome**, not evidence for a separate kind of expected value.

```bash
python src/cli.py --simulate 200000 --worlds 10000
python src/audit.py
```

## Historical check: useful context, no “due numbers”

With the optional Kaggle-format `649.csv` stored at `data/raw/649.csv`:

```bash
python src/cli.py --ticket 3 12 19 27 33 41 --check-history
```

The loader validates the required six draw columns, numeric integer values, 1–49 range and within-draw distinctness before comparing unordered combinations.

Under the project's independent-uniform-draw model, an exact combination's past frequency does **not** change its next-draw probability. The historical check illustrates the gambler's-fallacy point; it does not prove the real generating mechanism is independent or uniform.

## A final strategy nuance

All valid number combinations have the same probability of being drawn under this model, so number selection cannot improve the chance that your combination is selected.

That is narrower than saying “no strategy can affect payout”. Real jackpots may be shared, and player number popularity can affect split risk conditional on winning. This repository does not model player-choice behaviour or shared jackpots, so it does not make that broader claim.

## Tests

The archived version had **5 tests**. The audited version has **20 tests**, covering the exact match-probability partition, same-draw versus repeated-play estimands, EV reconstruction, finite-horizon identities, simulation sanity, invalid-domain handling, ticket validation and historical-data validation.

```bash
pytest -q
```

See [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) for the full assumptions and claim boundaries.

## Licence

MIT, see [LICENSE](LICENSE).
