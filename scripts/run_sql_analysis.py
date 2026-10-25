
from pathlib import Path

import duckdb
from tabulate import tabulate


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "bike_trips.parquet"
DB_PATH = PROJECT_ROOT / "data" / "analytics.duckdb"
SQL_DIR = PROJECT_ROOT / "sql"


def print_query_results(connection, query):
    """Execute a query and display results as a formatted table."""
    result = connection.execute(query)

    if result.description is None:
        return

    columns = [column[0] for column in result.description]
    rows = result.fetchall()

    if not rows:
        print("(No rows returned)")
        return

    print(
        tabulate(
            rows,
            headers=columns,
            tablefmt="rounded_grid",
            showindex=False,
        )
    )


def setup_database(connection):
    """Create a view over the cleaned Parquet dataset."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Cleaned Parquet file not found: {DATA_PATH}\n"
            "Run: python -m scripts.run_pipeline"
        )

    parquet_path = DATA_PATH.as_posix().replace("'", "''")

    connection.execute(
        f"""
        CREATE OR REPLACE VIEW bike_trips AS
        SELECT *
        FROM read_parquet('{parquet_path}')
        """
    )


def run_diagnostics(connection):
    """Display the dataset schema, row count, and sample records."""
    print("\n=== DATASET DIAGNOSTICS ===")

    print("\n--- Dataset schema ---")
    schema = connection.execute(
        "DESCRIBE SELECT * FROM bike_trips"
    ).fetchall()

    print(
        tabulate(
            [(row[0], row[1]) for row in schema],
            headers=["Column", "Data Type"],
            tablefmt="rounded_grid",
        )
    )

    print("\n--- Total number of trips ---")
    print_query_results(
        connection,
        "SELECT COUNT(*) AS total_trips FROM bike_trips",
    )

    print("\n--- First 10 trips ---")
    print_query_results(
        connection,
        "SELECT * FROM bike_trips LIMIT 10",
    )


def run_sql_files(connection):
    """Execute all SQL files in alphabetical order."""
    if not SQL_DIR.exists():
        raise FileNotFoundError(
            f"SQL directory not found: {SQL_DIR}"
        )

    sql_files = sorted(SQL_DIR.glob("*.sql"))

    if not sql_files:
        raise FileNotFoundError(
            f"No SQL files found in: {SQL_DIR}"
        )

    print("\n=== SQL ANALYSIS ===")

    for sql_file in sql_files:
        print(f"\n--- {sql_file.name} ---")

        sql_text = sql_file.read_text(encoding="utf-8")

        statements = [
            statement.strip()
            for statement in sql_text.split(";")
            if statement.strip()
        ]

        for statement in statements:
            print_query_results(connection, statement)


def main():
    """Run database setup, diagnostics, and SQL analyses."""
    connection = duckdb.connect(str(DB_PATH))

    try:
        setup_database(connection)
        run_diagnostics(connection)
        run_sql_files(connection)

        print("\nAnalysis completed successfully.")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
