from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tree_sitter import Language

def language() -> "Language": ...

__all__ = ["language"]
