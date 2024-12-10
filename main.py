#!/usr/bin/env python

import sys
import os
import argparse

from cli import main as cli_main
from bot import main as bot_main

CLI = 'cli'
TELEGRAM = 'telegram'


def main():
    parser = argparse.ArgumentParser(
        description='Start the chatbot or Telegram bot')

    parser.add_argument('--mode',
                        choices=[CLI, TELEGRAM],
                        default=CLI,
                        help='Run in chat or Telegram bot mode')

    args = parser.parse_args()

    if args.mode == CLI:
        cli_main()
    elif args.mode == TELEGRAM:
        bot_main()


if __name__ == '__main__':
    main()
