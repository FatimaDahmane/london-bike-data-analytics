import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def load_csv(path: str | Path) -> pd.DataFrame:
    """Load a CSV file and report useful errors."""
    path = Path(path)

    if not path.is_file():
        raise FileNotFoundError(
            f"Input CSV file does not exist: {path}"
        )

    try:
        df = pd.read_csv(path)
    except (OSError, UnicodeError, pd.errors.ParserError) as exc:
        raise RuntimeError(
            f"Could not read input CSV file '{path}': {exc}"
        ) from exc

    logger.info("Loaded %s (%s rows)", path, len(df))
    return df