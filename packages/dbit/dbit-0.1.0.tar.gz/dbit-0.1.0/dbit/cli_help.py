HELP_BANNER = r"""
                 ____    ____     ___     _____
                |  _ \  | __ )   |_ _|   |_   _|
                | | | | |  _ \    | |      | |  
                | |_| | | |_) |   | |      | |  
                |____/  |____/   |___|     |_|  

         DBIT - Version Control for Your Database Schema
"""

HELP_USAGE = """
USAGE:
  dbit <command> [options]

COMMANDS:
  init                 Initialize dbit config in the current directory.
  connect              Connect to a database and save the connection string.
  disconnect           Remove the saved database connection.
  snapshot             Capture a schema snapshot and save it to disk.
  status               Show changes since last snapshot.
  log                  View schema change history.
  verify               Apply schema quality and verification rules.
  help                 Show this help message.

OPTIONS:
  --help, -h           Show this message and exit.

EXAMPLES:
  # Initialize a new dbit repository
  dbit init

  # Connect to a PostgreSQL database
  dbit connect --db-url postgresql://user:pass@localhost:5432/dbname

  # Take a schema snapshot
  dbit snapshot

  # Show changes since last snapshot
  dbit status

  # View schema change history
  dbit log

  # Verify schema quality
  dbit verify

  # Disconnect from the database
  dbit disconnect

  # Show this help message
  dbit help
  dbit --help
  dbit -h
"""

def print_help():
    print(HELP_BANNER)
    print(HELP_USAGE)
