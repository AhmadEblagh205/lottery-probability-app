# Changelog

## 0.4.0 — defensibility audit

- separated N distinct tickets in one draw from N independent plays across draws;
- replaced silent ticket-count clipping with explicit domain validation;
- replaced the misleading “experienced EV”/single-seed convergence story with exact finite-horizon diagnostics and repeated-world simulation;
- added exact match counts for k=0..6 and a full probability-partition test;
- clarified that the fixed payout table is illustrative rather than a current real-lottery EV;
- narrowed the “no strategy changes it” claim to the equal draw probability of valid combinations, noting that real shared jackpots can introduce split-risk effects outside this model;
- added strict historical CSV validation;
- added methodology documentation and expanded the tests from 5 to 20.

## 0.3.0, update round 9

Added a simulation flag. In the archived version this was described as convergence to an “experienced EV”; the v0.4 audit retires that interpretation and keeps simulation only as a finite-horizon distribution illustration.

## 0.2.0, update round 3

Added expected value against illustrative prize tiers.

## 0.1.0

Initial release.
