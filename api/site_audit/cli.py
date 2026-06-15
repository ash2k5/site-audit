import argparse
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from .audit import build_report, safe_filename
from .pdf_generator import generate_pdf


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="site-audit",
        description="AI Site Audit Generator: produce a PDF audit from a URL.",
    )
    parser.add_argument("url", help="Website URL to audit (e.g. example.com)")
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output PDF path (default: audit_<domain>.pdf)",
    )
    parser.add_argument(
        "--no-screenshot",
        action="store_true",
        help="Skip the homepage screenshot capture",
    )
    parser.add_argument(
        "--allow-private",
        action="store_true",
        help="Allow auditing private or loopback addresses (local dev)",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)
    load_dotenv()

    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        print(
            "Error: GROQ_API_KEY is not set. Copy .env.example to .env and add your key.",
            file=sys.stderr,
        )
        sys.exit(1)

    output = args.output or safe_filename(args.url)
    try:
        report = build_report(
            args.url,
            groq_key=groq_key,
            pagespeed_key=os.getenv("PAGESPEED_API_KEY"),
            allow_private=args.allow_private,
        )
        generate_pdf(report, output, skip_screenshot=args.no_screenshot)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(Path(output).resolve())


if __name__ == "__main__":
    main()
