"""Simple migration script that runs alembic directly."""
import os
import subprocess
import sys

# Set the database URL for Neon app database
os.environ["DATABASE_URL"] = "postgresql://neondb_owner:npg_vWZYtS5boX7L@ep-purple-cake-aeu6ev2g-pooler.c-2.us-east-2.aws.neon.tech/app"

def main():
    """Run alembic upgrade."""
    # Change to the backend directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Update alembic.ini with the correct URL temporarily
    result = subprocess.run(
        [
            "alembic",
            "-x", f"sqlalchemy.url={os.environ['DATABASE_URL']}",
            "upgrade", "head"
        ],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
