"""CLI for an illustrative 6-from-49 probability/awareness engine."""
import argparse

from probability import (
    distinct_ticket_coverage_probability,
    expected_value,
    lifetime_horizon,
    match_probability,
    one_in,
    one_ticket_probability,
    repeated_play_jackpot_probability,
    simulate_lifetimes,
    validate_ticket,
)


def _positive_or_zero_float(value: str) -> float:
    x = float(value)
    if x < 0:
        raise argparse.ArgumentTypeError("value must be non-negative")
    return x


def main():
    ap = argparse.ArgumentParser(
        description="Exact 6-from-49 combinatorics with an illustrative payout model."
    )
    ap.add_argument("--ticket", nargs=6, type=int,
                    help="your 6 numbers (1-49)")
    ap.add_argument("--tickets", type=int,
                    help="N distinct tickets in one draw (coverage probability)")
    ap.add_argument("--plays", type=int,
                    help="N independent plays/draws (chance of >=1 jackpot)")
    ap.add_argument("--simulate", type=int, metavar="N",
                    help="simulate N independent plays per finite-horizon world")
    ap.add_argument("--worlds", type=int, default=10_000,
                    help="number of worlds for --simulate (default: 10000)")
    ap.add_argument("--ev", action="store_true",
                    help="EV under the repository's illustrative fixed-prize table")
    ap.add_argument("--ticket-price", type=_positive_or_zero_float, default=2.0)
    ap.add_argument("--match", type=int, choices=range(0, 7),
                    help="probability of matching exactly K numbers")
    ap.add_argument("--check-history", action="store_true",
                    help="check the ticket against optional data/raw/649.csv")
    args = ap.parse_args()

    if args.simulate is not None:
        r = simulate_lifetimes(args.simulate, args.worlds, args.ticket_price)
        h = lifetime_horizon(args.simulate, args.ticket_price)
        print(f"{r['worlds']:,} simulated worlds x {r['plays_per_world']:,} plays")
        print(f"Median realised loss/play: {r['median_loss_per_play']:.4f}")
        print(f"Mean realised loss/play:   {r['mean_loss_per_play']:.4f}")
        print(f"Exact unconditional expected loss/play: "
              f"{h['unconditional_expected_loss_per_play']:.4f}")
        print(f"Exact P(no jackpot over horizon): "
              f"{h['no_jackpot_probability']:.2%}")
        print("The mean and the typical finite-horizon outcome differ because the "
              "payout distribution is extremely right-skewed.")
        return

    if args.ev:
        r = expected_value(args.ticket_price)
        print("Illustrative fixed-prize model (not a current operator payout table):")
        print(f"Expected winnings per ticket: {r['expected_winnings']:.4f}")
        print(f"Expected loss per {r['ticket_price']:.2f} ticket: "
              f"{r['expected_loss']:.4f} "
              f"({r['loss_fraction_of_price']:.1%} of price)")
        for k in sorted(r["breakdown"], reverse=True):
            b = r["breakdown"][k]
            print(f"  match {k}: {one_in(b['probability'])} x "
                  f"{b['prize']:,.0f} = EV contribution {b['contribution']:.4f}")
        return

    ran = False
    if args.ticket:
        try:
            ticket = validate_ticket(args.ticket)
        except (TypeError, ValueError) as exc:
            raise SystemExit(str(exc)) from exc
        p = one_ticket_probability()
        print(f"Ticket {list(ticket)}:")
        print(f"  Jackpot probability: {p:.10f} ({one_in(p)})")
        print("  Under a uniform draw, every valid six-number combination has the "
              "same jackpot probability.")
        ran = True
        if args.check_history:
            from history import check_historical, load_draws
            draws = load_draws()
            n = check_historical(list(ticket), draws)
            print(f"  Historical occurrences in {len(draws):,} loaded draws: {n}")
            print("  Under independent uniform draws, this history does not change "
                  "the modelled next-draw probability.")

    if args.tickets is not None:
        try:
            p = distinct_ticket_coverage_probability(args.tickets)
        except (TypeError, ValueError) as exc:
            raise SystemExit(str(exc)) from exc
        print(f"{args.tickets:,} distinct tickets in ONE draw -> jackpot coverage "
              f"{p:.8f} ({one_in(p)})")
        ran = True

    if args.plays is not None:
        try:
            p = repeated_play_jackpot_probability(args.plays)
        except (TypeError, ValueError) as exc:
            raise SystemExit(str(exc)) from exc
        print(f"{args.plays:,} independent plays -> P(at least one jackpot) "
              f"{p:.8f} ({p:.4%})")
        ran = True

    if args.match is not None:
        p = match_probability(args.match)
        print(f"P(match exactly {args.match}) = {p:.8f} ({one_in(p)})")
        ran = True

    if not ran:
        ap.print_help()


if __name__ == "__main__":
    main()
