# coffy/nosql/engine.py
# author: nsarathy

"""
A simple NoSQL database engine.
This engine supports basic CRUD operations, querying with filters, and aggregation functions.
"""

import json
import os
import re


class QueryBuilder:
    """
    A class to build and execute queries on a collection of documents.
    Supports filtering, aggregation, and lookups.
    """

    def __init__(self, documents, all_collections=None):
        """
        Initialize the QueryBuilder with a collection of documents.
        documents -- List of documents (dictionaries) to query.
        all_collections -- Optional dictionary of all collections for lookups.
        """
        self.documents = documents
        self.filters = []
        self.current_field = None
        self.all_collections = all_collections or {}
        self._lookup_done = False
        self._lookup_results = None

    @staticmethod
    def _get_nested(doc, dotted_key):
        """
        Get a nested value from a document using a dotted key.
        dotted_key -- A string representing the path to the value, e.g., "a.b.c".
        Returns the value if found, otherwise None.
        """
        keys = dotted_key.split(".")
        for k in keys:
            if not isinstance(doc, dict) or k not in doc:
                return None
            doc = doc[k]
        return doc

    def where(self, field):
        """
        Set the current field for filtering.
        field -- The field to filter on, can be a dotted path like "a.b.c".
        Returns self to allow method chaining.
        """
        self.current_field = field
        return self

    # Comparison
    def eq(self, value):
        """
        Filter documents where the current field equals the given value.
        value -- The value to compare against.
        Returns self to allow method chaining.
        """
        return self._add_filter(
            lambda d: QueryBuilder._get_nested(d, self.current_field) == value
        )

    def ne(self, value):
        """
        Filter documents where the current field does not equal the given value.
        value -- The value to compare against.
        Returns self to allow method chaining.
        """
        return self._add_filter(
            lambda d: QueryBuilder._get_nested(d, self.current_field) != value
        )

    def gt(self, value):
        """
        Filter documents where the current field is greater than the given value.
        value -- The value to compare against.
        Returns self to allow method chaining.
        """
        return self._add_filter(
            lambda d: isinstance(
                QueryBuilder._get_nested(d, self.current_field), (int, float)
            )
            and QueryBuilder._get_nested(d, self.current_field) > value
        )

    def gte(self, value):
        """
        Filter documents where the current field is greater than or equal to the given value.
        value -- The value to compare against.
        Returns self to allow method chaining.
        """
        return self._add_filter(
            lambda d: isinstance(
                QueryBuilder._get_nested(d, self.current_field), (int, float)
            )
            and QueryBuilder._get_nested(d, self.current_field) >= value
        )

    def lt(self, value):
        """
        Filter documents where the current field is less than the given value.
        value -- The value to compare against.
        Returns self to allow method chaining.
        """
        return self._add_filter(
            lambda d: isinstance(
                QueryBuilder._get_nested(d, self.current_field), (int, float)
            )
            and QueryBuilder._get_nested(d, self.current_field) < value
        )

    def lte(self, value):
        """
        Filter documents where the current field is less than or equal to the given value.
        value -- The value to compare against.
        Returns self to allow method chaining.
        """
        return self._add_filter(
            lambda d: isinstance(
                QueryBuilder._get_nested(d, self.current_field), (int, float)
            )
            and QueryBuilder._get_nested(d, self.current_field) <= value
        )

    def in_(self, values):
        """
        Filter documents where the current field is in the given list of values.
        values -- The list of values to compare against.
        Returns self to allow method chaining.
        """
        return self._add_filter(
            lambda d: QueryBuilder._get_nested(d, self.current_field) in values
        )

    def nin(self, values):
        """
        Filter documents where the current field is not in the given list of values.
        values -- The list of values to compare against.
        Returns self to allow method chaining.
        """
        return self._add_filter(
            lambda d: QueryBuilder._get_nested(d, self.current_field) not in values
        )

    def matches(self, regex):
        """
        Filter documents where the current field matches the given regular expression.
        regex -- The regular expression to match against.
        Returns self to allow method chaining.
        """
        return self._add_filter(
            lambda d: re.search(
                regex, str(QueryBuilder._get_nested(d, self.current_field))
            )
        )

    def exists(self):
        """
        Filter documents where the current field exists.
        Returns self to allow method chaining.
        """
        return self._add_filter(
            lambda d: QueryBuilder._get_nested(d, self.current_field) is not None
        )

    # Logic grouping
    def _and(self, *fns):
        """
        Combine multiple filter functions with logical AND.
        fns -- Functions that take a QueryBuilder instance and modify its filters.
        Returns self to allow method chaining.
        """
        for fn in fns:
            sub = QueryBuilder(self.documents, self.all_collections)
            fn(sub)
            self.filters.append(lambda d, fs=sub.filters: all(f(d) for f in fs))
        return self

    def _not(self, *fns):
        """
        Combine multiple filter functions with logical NOT.
        fns -- Functions that take a QueryBuilder instance and modify its filters.
        Returns self to allow method chaining.
        """
        for fn in fns:
            sub = QueryBuilder(self.documents, self.all_collections)
            fn(sub)
            self.filters.append(lambda d, fs=sub.filters: not all(f(d) for f in fs))
        return self

    def _or(self, *fns):
        """
        Combine multiple filter functions with logical OR.
        fns -- Functions that take a QueryBuilder instance and modify its filters.
        Returns self to allow method chaining.
        """
        chains = []
        for fn in fns:
            sub = QueryBuilder(self.documents, self.all_collections)
            fn(sub)
            chains.append(sub.filters)
        self.filters.append(lambda d: any(all(f(d) for f in chain) for chain in chains))
        return self

    # Add filter
    def _add_filter(self, fn):
        """
        Add a filter function to the query.
        fn -- A function that takes a document and returns True if it matches the filter.
        Returns self to allow method chaining.
        """
        negate = getattr(self, "_negate", False)
        self._negate = False
        self.filters.append(lambda d: not fn(d) if negate else fn(d))
        return self

    # Core execution
    def run(self, fields=None):
        """
        Execute the query and return the results.
        fields -- Optional list of fields to project in the results.
            If provided, only these fields will be included in the returned documents.
            Otherwise, the full documents will be returned.
        Returns a DocList containing the matching documents.
        """
        results = [doc for doc in self.documents if all(f(doc) for f in self.filters)]
        if self._lookup_done:
            results = self._lookup_results

        if fields is not None:
            projected = []
            for doc in results:
                proj = {}
                for f in fields:
                    value = QueryBuilder._get_nested(doc, f)
                    proj[f] = value
                projected.append(proj)
            return DocList(projected)

        return DocList(results)

    def update(self, changes):
        """
        Update documents that match the current filters with the given changes.
        changes -- A dictionary of fields to update in the matching documents.
        Returns a dictionary with the count of updated documents.
        """
        count = 0
        for doc in self.documents:
            if all(f(doc) for f in self.filters):
                doc.update(changes)
                count += 1
        return {"updated": count}

    def delete(self):
        """
        Delete documents that match the current filters.
        Returns a dictionary with the count of deleted documents.
        """
        before = len(self.documents)
        self.documents[:] = [
            doc for doc in self.documents if not all(f(doc) for f in self.filters)
        ]
        return {"deleted": before - len(self.documents)}

    def replace(self, new_doc):
        """
        Replace documents that match the current filters with a new document.
        new_doc -- The new document to replace matching documents with.
        Returns a dictionary with the count of replaced documents.
        """
        replaced = 0
        for i, doc in enumerate(self.documents):
            if all(f(doc) for f in self.filters):
                self.documents[i] = new_doc
                replaced += 1
        return {"replaced": replaced}

    def count(self):
        """
        Count the number of documents that match the current filters.
        Returns the count of matching documents.
        """
        return len(self.run())

    def first(self):
        """
        Get the first document that matches the current filters.
        Returns the first matching document, or None if no documents match.
        """
        return next(iter(self.run()), None)

    # Aggregates
    def sum(self, field):
        """
        Calculate the sum of a numeric field across all matching documents.
        field -- The field to sum.
        Returns the total sum of the field values.
            If no documents match or the field is not numeric, returns 0.
        """
        return sum(
            doc.get(field, 0)
            for doc in self.run()
            if isinstance(doc.get(field), (int, float))
        )

    def avg(self, field):
        """
        Calculate the average of a numeric field across all matching documents.
        field -- The field to average.
        Returns the average of the field values.
            If no documents match or the field is not numeric, returns 0.
        """
        values = [
            doc.get(field)
            for doc in self.run()
            if isinstance(doc.get(field), (int, float))
        ]
        return sum(values) / len(values) if values else 0

    def min(self, field):
        """
        Find the minimum value of a numeric field across all matching documents.
        field -- The field to find the minimum of.
        Returns the minimum value of the field.
            If no documents match or the field is not numeric, returns None.
        """
        values = [
            doc.get(field)
            for doc in self.run()
            if isinstance(doc.get(field), (int, float))
        ]
        return min(values) if values else None

    def max(self, field):
        """
        Find the maximum value of a numeric field across all matching documents.
        field -- The field to find the maximum of.
        Returns the maximum value of the field.
            If no documents match or the field is not numeric, returns None.
        """
        values = [
            doc.get(field)
            for doc in self.run()
            if isinstance(doc.get(field), (int, float))
        ]
        return max(values) if values else None

    # Lookup
    def lookup(self, foreign_collection_name, local_key, foreign_key, as_field):
        """
        Perform a lookup to enrich documents with related data from another collection.
        foreign_collection_name -- The name of the foreign collection to join with.
        local_key -- The key in the local documents to match against the foreign collection.
        foreign_key -- The key in the foreign documents to match against the local collection.
        as_field -- The name of the field to add to the local documents with the joined data.
        Returns self to allow method chaining.
        """
        foreign_docs = self.all_collections.get(foreign_collection_name, [])
        fk_map = {doc[foreign_key]: doc for doc in foreign_docs}
        enriched = []
        for doc in self.run():
            joined = fk_map.get(doc.get(local_key))
            if joined:
                doc = dict(doc)  # copy
                doc[as_field] = joined
                enriched.append(doc)
        self._lookup_done = True
        self._lookup_results = enriched
        return self

    # Merge
    def merge(self, fn):
        """
        Merge the results of the query with additional data.
        fn -- A function that takes a document and returns a dictionary of fields to update.
        Returns self to allow method chaining.
        """
        docs = self._lookup_results if self._lookup_done else self.run()
        merged = []
        for doc in docs:
            new_doc = dict(doc)
            new_doc.update(fn(doc))
            merged.append(new_doc)
        self._lookup_done = True
        self._lookup_results = merged
        return self


_collection_registry = {}


class CollectionManager:
    """
    Manage a NoSQL collection, providing methods for querying and manipulating documents.
    """

    def __init__(self, name: str, path: str = None):
        """
        Initialize a collection manager for a NoSQL collection.
        name -- The name of the collection.
        path -- Optional path to a JSON file where the collection data is stored.
        """
        self.name = name
        self.in_memory = False

        if path:
            if not path.endswith(".json"):
                raise ValueError("Path must be to a .json file")
            self.path = path
        else:
            self.in_memory = True

        self.documents = []
        self._load()
        _collection_registry[name] = self.documents

    def _load(self):
        """
        Load the collection data from the JSON file.
        If the file does not exist, create an empty collection.
        If in_memory is True, initialize an empty collection.
        """
        if self.in_memory:
            self.documents = []
        else:
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.documents = json.load(f)
            except FileNotFoundError:
                os.makedirs(os.path.dirname(self.path), exist_ok=True)
                self.documents = []

    def _save(self):
        """
        Save the collection data to the JSON file.
        If in_memory is True, this method does nothing.
        """
        if not self.in_memory:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.documents, f, indent=4)

    def add(self, document: dict):
        """
        Add a document to the collection.
        document -- The document to add, must be a dictionary.
        Returns a dictionary with the count of inserted documents.
        """
        self.documents.append(document)
        self._save()
        return {"inserted": 1}

    def add_many(self, docs: list[dict]):
        """
        Add multiple documents to the collection.
        docs -- A list of documents to add, each must be a dictionary.
        Returns a dictionary with the count of inserted documents.
        """
        self.documents.extend(docs)
        self._save()
        return {"inserted": len(docs)}

    def where(self, field):
        """
        Start a query to filter documents based on a field.
        field -- The field to filter on.
        Returns a QueryBuilder instance to build the query.
        """
        return QueryBuilder(self.documents, all_collections=_collection_registry).where(
            field
        )

    def match_any(self, *conditions):
        """
        Start a query to match any of the specified conditions.
        conditions -- Functions that take a QueryBuilder instance and modify its filters.
        Returns a QueryBuilder instance with the combined conditions.
        """
        q = QueryBuilder(self.documents, all_collections=_collection_registry)
        return q._or(*conditions)

    def match_all(self, *conditions):
        """
        Start a query to match all of the specified conditions.
        conditions -- Functions that take a QueryBuilder instance and modify its filters.
        Returns a QueryBuilder instance with the combined conditions.
        """
        q = QueryBuilder(self.documents, all_collections=_collection_registry)
        return q._and(*conditions)

    def not_any(self, *conditions):
        """
        Start a query to negate any of the specified conditions.
        conditions -- Functions that take a QueryBuilder instance and modify its filters.
        Returns a QueryBuilder instance with the negated conditions.
        """
        q = QueryBuilder(self.documents, all_collections=_collection_registry)
        return q._not(lambda nq: nq._or(*conditions))

    def lookup(self, *args, **kwargs):
        """
        Perform a lookup to enrich documents with related data from another collection.
        args -- Positional arguments for the lookup.
        kwargs -- Keyword arguments for the lookup.
        Returns a QueryBuilder instance with the lookup applied.
        """
        return QueryBuilder(
            self.documents, all_collections=_collection_registry
        ).lookup(*args, **kwargs)

    def merge(self, *args, **kwargs):
        """
        Merge documents from another collection into this collection.
        args -- Positional arguments for the merge.
        kwargs -- Keyword arguments for the merge.
        Returns a QueryBuilder instance with the merge applied.
        """
        return QueryBuilder(self.documents, all_collections=_collection_registry).merge(
            *args, **kwargs
        )

    def sum(self, field):
        """
        Calculate the sum of a numeric field across all documents.
        field -- The field to sum.
        Returns the sum of the field values.
        """
        return QueryBuilder(self.documents).sum(field)

    def avg(self, field):
        """
        Calculate the average of a numeric field across all documents.
        field -- The field to average.
        Returns the average of the field values.
        """
        return QueryBuilder(self.documents).avg(field)

    def min(self, field):
        """
        Calculate the minimum of a numeric field across all documents.
        field -- The field to find the minimum.
        Returns the minimum of the field values.
        """
        return QueryBuilder(self.documents).min(field)

    def max(self, field):
        """
        Calculate the maximum of a numeric field across all documents.
        field -- The field to find the maximum.
        Returns the maximum of the field values.
        """
        return QueryBuilder(self.documents).max(field)

    def count(self):
        """
        Count the number of documents in the collection.
        Returns the count of documents.
        """
        return QueryBuilder(self.documents).count()

    def first(self):
        """
        Get the first document in the collection.
        Returns the first document or None if the collection is empty.
        """
        return QueryBuilder(self.documents).first()

    def clear(self):
        """
        Clear all documents from the collection.
        Returns a dictionary with the count of cleared documents.
        """
        count = len(self.documents)
        self.documents = []
        self._save()
        return {"cleared": count}

    def export(self, path):
        """
        Export the collection to a JSON file.
        path -- The file path to export the collection.
        """
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.documents, f, indent=4)

    def import_(self, path):
        """
        Import documents from a JSON file into the collection.
        path -- The file path to import the collection from.
        If the file does not exist, it raises a FileNotFoundError.
        """
        with open(path, "r", encoding="utf-8") as f:
            self.documents = json.load(f)
        self._save()

    def all(self):
        """
        Get all documents in the collection.
        Returns a list of all documents.
        """
        return self.documents

    def save(self, path: str):
        """
        Save the current state of the collection to a JSON file.
        path -- The file path to save the collection.
        If the path does not end with .json, it raises a ValueError.
        """
        if not path.endswith(".json"):
            raise ValueError("Invalid file format. Please use a .json file.")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.documents, f, indent=4)

    def all_docs(self):
        """
        Get all documents in the collection.
        Returns a list of all documents.
        """
        return self.documents


class DocList:
    """
    A class to represent a list of documents with additional utility methods.
    Provides methods to iterate, access by index, get length, and convert to JSON.
    """

    def __init__(self, docs: list[dict]):
        """
        Initialize the DocList with a list of documents.
        docs -- A list of documents (dictionaries) to store in the DocList.
        """
        self._docs = docs

    def __iter__(self):
        """
        Return an iterator over the documents in the DocList.
        """
        return iter(self._docs)

    def __getitem__(self, index):
        """
        Get a document by index.
        index -- The index of the document to retrieve.
        Returns the document at the specified index.
        """
        return self._docs[index]

    def __len__(self):
        """
        Get the number of documents in the DocList.
        Returns the count of documents.
        """
        return len(self._docs)

    def __repr__(self):
        """
        Return a string representation of the DocList.
        If the DocList is empty, it returns "<empty result>".
        Otherwise, it formats the documents as a table with headers.
        """
        if not self._docs:
            return "<empty result>"
        keys = list(self._docs[0].keys())
        header = " | ".join(keys)
        line = "-+-".join("-" * len(k) for k in keys)
        rows = []
        for doc in self._docs:
            row = " | ".join(str(doc.get(k, "")) for k in keys)
            rows.append(row)
        return f"{header}\n{line}\n" + "\n".join(rows)

    def to_json(self, path: str):
        """
        Save the documents in the DocList to a JSON file.
        path -- The file path to save the documents.
        """
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._docs, f, indent=4)

    def as_list(self):
        """
        Convert the DocList to a regular list of documents.
        """
        return self._docs
