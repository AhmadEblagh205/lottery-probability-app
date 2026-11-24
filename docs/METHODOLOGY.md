# Methodology — Lottery Probability Engine

## Scope

This repository is an educational probability/decision-communication project for an **illustrative uniform 6-from-49 draw**. It is not a model of the complete current rules, prize sharing or expected value of any named lottery operator.

The core assumptions are:

1. Six distinct numbers are drawn uniformly without replacement from 1–49.
2. A ticket is an unordered six-number combination.
3. Successive draws are independent in the mathematical model.
4. The optional expected-value example uses a fixed illustrative prize table. Real games can have changing/shared jackpots, bonus games and other rules.

## Exact combinatorics

There are

\[
\binom{49}{6}=13,983,816
\]

possible unordered tickets. For a fixed ticket, the number of draws matching exactly \(k\) of its six numbers is

\[
\binom{6}{k}\binom{43}{6-k},
\]

so

\[
P(K=k)=\frac{\binom{6}{k}\binom{43}{6-k}}{\binom{49}{6}}.
\]

The integer event counts are exact. Python floats are used only to present ratios/expected values.

## Two different meanings of “N tickets”

These must not be conflated.

### N distinct tickets in one draw

The jackpot events are mutually exclusive, so

\[
P(\text{jackpot})=\frac{N}{\binom{49}{6}}, \qquad 0\le N\le \binom{49}{6}.
\]

Buying every possible distinct ticket covers the entire draw space and gives probability 1 of holding the jackpot combination (ignoring prize sharing/cost).

### N independent one-ticket plays across draws

Now the same ticket-level event is repeated independently, so

\[
P(\text{at least one jackpot})
=1-(1-p)^N,
\qquad p=\frac{1}{\binom{49}{6}}.
\]

At \(N=13,983,816\), the first experiment gives 100% coverage, whereas repeated independent play gives only about 63.2% probability of at least one jackpot. The difference is an estimand difference, not a numerical approximation issue.

## Expected value and the typical finite horizon

The illustrative fixed prize table is:

- 6 matches: £5,000,000
- 5 matches: £1,750
- 4 matches: £140
- 3 matches: £30

With a £2 ticket this produces expected winnings of about £1.055 and expected loss of about £0.945 per play. **This is a toy payout model, not a claim about the current EV of Canadian Lotto 6/49 or any other real lottery.**

The jackpot contributes roughly one third of the toy model's expected winnings but is extremely rare. Over 200,000 independent plays:

- expected jackpot count is only about 0.0143;
- probability of no jackpot is about 98.58%;
- conditional on no jackpot, expected loss is about £1.303 per play.

Therefore the *typical finite-horizon realised outcome* can sit far from the unconditional arithmetic expectation. That does not create a second “experienced EV”. The expectation remains £0.945 loss per play; the gap is caused by a highly skewed payout distribution whose mean is influenced by rare jackpot worlds.

A repeated-world Monte Carlo is included only to visualise this skew. It does not replace the exact calculations.

## Historical checks and the gambler's fallacy

The optional history function asks only whether the exact unordered ticket appeared in a supplied historical CSV. Under the model of independent uniform draws,

\[
P(\text{next draw}=A\mid\text{past draws})=P(\text{next draw}=A)
\]

for every valid combination \(A\). A number being “due”, “hot” or previously successful does not change the next-draw probability under those assumptions.

This is a **model statement**. A history file can be useful for demonstrating the gambler's-fallacy lesson, but historical coincidence does not validate the independence/uniformity assumptions themselves.

## Number-selection strategies and shared jackpots

Under a uniform draw, every valid six-number combination has the same probability of being drawn. That means a number-selection strategy cannot improve the modelled probability of matching the drawn combination.

However, real jackpots may be shared among multiple winners. If other players choose some combinations more often than others, number popularity can affect the *conditional payout if you win*. This repository does not model player-choice distributions or jackpot splitting, so it deliberately avoids the broader claim that “no strategy can ever affect expected payout”.

## Validation

The audited test suite covers:

- total combination count and exact-match partition;
- known hypergeometric event counts;
- same-draw coverage versus repeated-play probability;
- invalid domains rather than silent clipping;
- exact EV reconstruction and input guards;
- finite-horizon jackpot/no-jackpot identities;
- independent-play horizon inversion;
- repeated-world simulation sanity;
- ticket validation;
- historical CSV schema, numeric, range and distinctness checks.
