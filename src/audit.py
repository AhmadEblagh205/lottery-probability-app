"""Deterministic/reproducible audit outputs used by the README."""
from probability import (
    TOTAL,
    DEFAULT_PRIZES,
    distinct_ticket_coverage_probability,
    expected_value,
    lifetime_horizon,
    match_probability,
    plays_for_jackpot_probability,
    repeated_play_jackpot_probability,
    simulate_lifetimes,
)


def main() -> None:
    print(f"Total unordered 6-from-49 tickets: {TOTAL:,}")
    print("Exact-match probabilities:")
    for k in range(7):
        p = match_probability(k)
        print(f"  k={k}: p={p:.12f}, 1/p={1/p:,.3f}")

    ev = expected_value(2.0)
    jackpot_ev = match_probability(6) * DEFAULT_PRIZES[6]
    print("\nIllustrative fixed-prize EV:")
    print(f"  expected winnings = {ev['expected_winnings']:.6f}")
    print(f"  expected loss = {ev['expected_loss']:.6f}")
    print(f"  loss fraction = {ev['loss_fraction_of_price']:.6%}")
    print(f"  jackpot contribution = {jackpot_ev:.6f} "
          f"({jackpot_ev/ev['expected_winnings']:.2%} of expected winnings)")

    n = 200_000
    h = lifetime_horizon(n, 2.0)
    print(f"\nFinite horizon: {n:,} independent plays")
    print(f"  P(at least one jackpot) = {h['jackpot_probability']:.6%}")
    print(f"  P(no jackpot) = {h['no_jackpot_probability']:.6%}")
    print(f"  expected jackpot count = {h['expected_jackpots']:.6f}")
    print(f"  unconditional expected loss/play = "
          f"{h['unconditional_expected_loss_per_play']:.6f}")
    print(f"  expected loss/play conditional on no jackpot = "
          f"{h['no_jackpot_expected_loss_per_play']:.6f}")

    sim = simulate_lifetimes(n, n_worlds=200_000, ticket_price=2.0, seed=25)
    print("\n200,000-world Monte Carlo (distribution illustration):")
    print(f"  median loss/play = {sim['median_loss_per_play']:.6f}")
    print(f"  mean loss/play = {sim['mean_loss_per_play']:.6f}")
    print(f"  jackpot-world fraction = {sim['jackpot_world_fraction']:.6%}")
    print(f"  2.5%-97.5% loss/play quantiles = "
          f"[{sim['q025_loss_per_play']:.6f}, {sim['q975_loss_per_play']:.6f}]")

    same_draw = distinct_ticket_coverage_probability(TOTAL)
    repeated = repeated_play_jackpot_probability(TOTAL)
    print(f"\nSame-draw vs repeated-play estimands at N=TOTAL={TOTAL:,}:")
    print(f"  N distinct tickets in one draw = {same_draw:.6%}")
    print(f"  N independent one-ticket plays = {repeated:.6%}")

    print("\nIndependent-play horizons:")
    for target in (0.50, 0.95, 0.99):
        print(f"  {target:.0%} chance of >=1 jackpot: "
              f"{plays_for_jackpot_probability(target):,} plays")


if __name__ == "__main__":
    main()
