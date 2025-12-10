from typing import Optional
import sqlite3


def row_to_dict(row: Optional[sqlite3.Row]):
    return dict(row) if row else None
