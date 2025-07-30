# coffy/nosql/__init__.py
# author: nsarathy

from .engine import CollectionManager
from .atomicity import _atomic_save as _atomic_save
from .index_engine import IndexManager as IndexManager


def db(collection_name: str, path: str = None):
    return CollectionManager(collection_name, path=path)


__all__ = ["db", "CollectionManager", "_atomic_save", "IndexManager"]
