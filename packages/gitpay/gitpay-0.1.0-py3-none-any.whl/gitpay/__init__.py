import argparse
import os

def get_terminal_url(recipient: str, amount: float) -> str:
    return f"https://terminal.merit.systems/{recipient}/pay?amount={amount}"

def positive_float(value: str) -> float:
    try:
        float_value = float(value)
        if float_value <= 0:
            raise argparse.ArgumentTypeError(f"Amount must be positive, got {float_value}")
        return float_value
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid float value: {value}")


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Pay anyone or anything on GitHub"
    )
    parser.add_argument(
        "recipient",
        type=str,
        help="GitHub username of the recipient (e.g., @fmhall)",
    )

    parser.add_argument(
        "amount",
        type=positive_float,
        help="Amount to pay in dollars (must be positive)",
    )

    args = parser.parse_args()
    args.recipient = args.recipient.strip("@")

    print(f"Paying {args.amount} to {args.recipient}, open this link in your browser:")
    print(f"https://terminal.merit.systems/{args.recipient}/pay?amount={args.amount}")
    os.system(f"open {get_terminal_url(args.recipient, args.amount)}")