"""
Management Command: wipe_db
Description:
    This command completely wipes all data from the database.
    It uses Django's built-in 'flush' command to remove all data from every model.
    You can run it interactively or bypass confirmation using the '--noinput' flag.
Usage:
    python manage.py wipe_db
    python manage.py wipe_db --noinput
"""

import sys
from django.core.management.base import BaseCommand
from django.core import management


class Command(BaseCommand):
    help = "Wipes EVERYTHING off the database (all data from all models will be deleted)."

    def add_arguments(self, parser):
        parser.add_argument(
            '--noinput',
            action='store_true',
            help="Bypass the confirmation prompt and wipe the database without interactive confirmation."
        )

    def handle(self, *args, **options):
        noinput = options['noinput']
        if not noinput:
            confirm = input(
                "WARNING: This will permanently delete ALL data from the database. "
                "Type 'yes' to continue: "
            )
            if confirm.lower() != 'yes':
                self.stdout.write("Aborting wipe operation.")
                sys.exit(0)
        # Execute the flush command with interactive set to False.
        management.call_command('flush', interactive=False)
        self.stdout.write(self.style.SUCCESS("Successfully wiped everything off the database."))
