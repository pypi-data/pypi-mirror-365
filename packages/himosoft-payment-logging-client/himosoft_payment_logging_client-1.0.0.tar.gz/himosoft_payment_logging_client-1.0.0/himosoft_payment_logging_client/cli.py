#!/usr/bin/env python3
"""
Command-line interface for the Himosoft Payment Logging Client.
"""

import argparse
import json
import sys
from typing import Dict, Any

from . import PaymentLogger, __version__
from .exceptions import PaymentLoggerError


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Himosoft Payment Logging Client - Log payments to the Himosoft Payment Logging API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Log a successful payment
  himosoft-payment-logging-client log-payment \\
    --user "john@example.com" \\
    --package "Premium Plan" \\
    --amount 99.99 \\
    --status paid \\
    --trx-id "TXN123456" \\
    --payment-method "credit_card" \\
    --gateway-name "Stripe" \\
    --gateway-log '{"charge_id": "ch_123"}'

  # Test connection
  himosoft-payment-logging-client test-connection

  # Show version
  himosoft-payment-logging-client --version
        """
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"himosoft-payment-logging-client {__version__}"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Log payment command
    log_parser = subparsers.add_parser(
        "log-payment",
        help="Log a payment transaction"
    )
    
    log_parser.add_argument(
        "--user",
        required=True,
        help="User identifier (email, username, or phone)"
    )
    
    log_parser.add_argument(
        "--package",
        required=True,
        help="Package or plan name"
    )
    
    log_parser.add_argument(
        "--amount",
        required=True,
        type=float,
        help="Payment amount (positive number)"
    )
    
    log_parser.add_argument(
        "--status",
        required=True,
        choices=["paid", "failed", "canceled", "refunded"],
        help="Payment status"
    )
    
    log_parser.add_argument(
        "--trx-id",
        help="Transaction ID (required for 'paid' and 'refunded' status)"
    )
    
    log_parser.add_argument(
        "--payment-method",
        help="Payment method used (e.g., 'credit_card', 'paypal')"
    )
    
    log_parser.add_argument(
        "--gateway-name",
        help="Payment gateway name (e.g., 'Stripe', 'PayPal')"
    )
    
    log_parser.add_argument(
        "--gateway-log",
        help="Complete gateway response (JSON string)"
    )
    
    log_parser.add_argument(
        "--server-url",
        help="Payment server URL (overrides environment variable)"
    )
    
    log_parser.add_argument(
        "--api-key",
        help="Platform API key (overrides environment variable)"
    )
    
    log_parser.add_argument(
        "--output",
        choices=["json", "text"],
        default="text",
        help="Output format (default: text)"
    )
    
    # Test connection command
    test_parser = subparsers.add_parser(
        "test-connection",
        help="Test connection to the payment server"
    )
    
    test_parser.add_argument(
        "--server-url",
        help="Payment server URL (overrides environment variable)"
    )
    
    test_parser.add_argument(
        "--api-key",
        help="Platform API key (overrides environment variable)"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == "log-payment":
            log_payment(args)
        elif args.command == "test-connection":
            test_connection(args)
    except PaymentLoggerError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def log_payment(args):
    """Log a payment transaction."""
    # Parse gateway_log if provided
    gateway_log = None
    if args.gateway_log:
        try:
            gateway_log = json.loads(args.gateway_log)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in --gateway-log: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Initialize logger
    logger = PaymentLogger(
        server_url=args.server_url,
        api_key=args.api_key
    )
    
    # Log the payment
    result = logger.log_payment(
        user=args.user,
        package=args.package,
        amount=args.amount,
        status=args.status,
        trx_id=args.trx_id,
        payment_method=args.payment_method,
        gateway_name=args.gateway_name,
        gateway_log=gateway_log
    )
    
    # Output result
    if args.output == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"✅ Payment logged successfully!")
        print(f"   Status: {result.get('status', 'unknown')}")
        print(f"   Message: {result.get('message', 'No message')}")
        if result.get('trx_id'):
            print(f"   Transaction ID: {result['trx_id']}")
        if result.get('payment_id'):
            print(f"   Payment ID: {result['payment_id']}")


def test_connection(args):
    """Test connection to the payment server."""
    logger = PaymentLogger(
        server_url=args.server_url,
        api_key=args.api_key
    )
    
    try:
        if logger.test_connection():
            print("✅ Connection test successful")
        else:
            print("⚠️  Connection test failed")
            sys.exit(1)
    except PaymentLoggerError as e:
        print(f"❌ Connection test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 