# coffy/sql/__init__.py
# author: nsarathy

from .engine import execute_query, initialize


def init(path: str = None):
    """Initialize the SQL engine with the given path."""
    initialize(path)


def query(sql: str):
    """Execute a SQL query and return the results."""
    return execute_query(sql)


__all__ = ["init", "query", "execute_query", "initialize"]
