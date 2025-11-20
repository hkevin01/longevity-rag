"""Neo4j connector stub.

Provides a GraphClient class that will connect to Neo4j. For MVP this is a
stub that raises a clear error if Neo4j settings are missing.
"""

from __future__ import annotations

from typing import Optional


class GraphClient:
    def __init__(self, uri: Optional[str] = None, user: Optional[str] = None, password: Optional[str] = None):
        if not uri:
            raise RuntimeError("Neo4j URI not configured. Knowledge graph is disabled in MVP.")
        # Implementation placeholder

