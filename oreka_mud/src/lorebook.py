"""Lorebook — keyword-triggered lore injection for NPC prompts.

Inspired by NovelAI's Lorebook system.  Instead of cramming the
entire Canon Bible into every prompt (expensive, noisy), the Lorebook
holds ~50-80 short lore entries, each tagged with trigger keywords.
When a player mentions a keyword in conversation, the matching entry
injects into the AI's prompt context.  Entries that aren't triggered
don't waste tokens.

Data lives in ``data/lorebook.json``.  Each entry:

    {
        "id":        "aldenheim",
        "keywords":  ["aldenheim", "fall of aldenheim", "cinvarin", "five witnesses"],
        "priority":  8,           # 1-10, higher = injected first if budget tight
        "max_tokens": 200,        # approximate budget for this entry
        "content":   "Aldenheim was a Vestri dwarf-hold where five druids..."
    }

The scanner checks the player's latest message AND the last few
conversation turns for keyword matches, then returns the top entries
sorted by priority, capped at a configurable total token budget.

Usage in the prompt builder:

    from src.lorebook import get_lorebook, scan_for_lore
    entries = scan_for_lore(conversation_text, max_total_tokens=800)
    if entries:
        prompt_parts.append("\\nWORLD LORE (relevant to this conversation):")
        for entry in entries:
            prompt_parts.append(entry["content"])
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger("OrekaMUD.Lorebook")


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data",
                          "lorebook.json")

# Default maximum total tokens to inject per prompt turn
DEFAULT_MAX_TOTAL_TOKENS = 800

# Minimum keyword length to avoid false positives on short words
MIN_KEYWORD_LENGTH = 3


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

class Lorebook:
    """In-memory index of lore entries with keyword lookup."""

    def __init__(self):
        self.entries: List[Dict[str, Any]] = []
        # keyword (lowercased) -> list of entry indices
        self._keyword_index: Dict[str, List[int]] = {}
        self._loaded = False

    def load(self, path: Optional[str] = None) -> None:
        path = path or _DATA_PATH
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning("lorebook.json load failed: %s", e)
            self.entries = []
            self._loaded = True
            return

        raw = data if isinstance(data, list) else data.get("entries", [])
        self.entries = []
        self._keyword_index = {}

        for i, entry in enumerate(raw):
            if not isinstance(entry, dict):
                continue
            # Normalize
            entry.setdefault("id", f"entry_{i}")
            entry.setdefault("keywords", [])
            entry.setdefault("priority", 5)
            entry.setdefault("max_tokens", 200)
            entry.setdefault("content", "")
            self.entries.append(entry)

            # Build keyword index
            for kw in entry["keywords"]:
                kw_lower = kw.strip().lower()
                if len(kw_lower) < MIN_KEYWORD_LENGTH:
                    continue
                self._keyword_index.setdefault(kw_lower, []).append(
                    len(self.entries) - 1
                )

        self._loaded = True
        logger.info("Lorebook: loaded %d entries with %d keywords",
                    len(self.entries), len(self._keyword_index))

    def reload(self) -> None:
        self._loaded = False
        self.load()


_lorebook: Optional[Lorebook] = None


def get_lorebook() -> Lorebook:
    global _lorebook
    if _lorebook is None:
        _lorebook = Lorebook()
        _lorebook.load()
    return _lorebook


# ---------------------------------------------------------------------------
# Keyword scanner
# ---------------------------------------------------------------------------

def _normalize_text(text: str) -> str:
    """Lowercase and strip punctuation for matching."""
    return re.sub(r"[^\w\s]", " ", text.lower())


def scan_for_lore(text: str, *,
                  max_total_tokens: int = DEFAULT_MAX_TOTAL_TOKENS,
                  exclude_ids: Optional[set] = None) -> List[Dict[str, Any]]:
    """Scan ``text`` for Lorebook keywords and return matching entries,
    sorted by priority (highest first), capped at ``max_total_tokens``.

    ``text`` should include the player's latest message AND recent
    conversation history for best recall.

    Returns a list of entry dicts (with ``id``, ``content``, ``priority``,
    ``max_tokens``, and ``matched_keywords``).
    """
    book = get_lorebook()
    if not book._loaded or not book.entries:
        return []

    normalized = _normalize_text(text)
    exclude = exclude_ids or set()

    # Find all matching entries
    matched_indices: Dict[int, List[str]] = {}  # entry_index -> [matched keywords]
    for kw, indices in book._keyword_index.items():
        # Check if the keyword appears as a whole word (or phrase) in the text
        # Use word-boundary-like check for single words; substring for phrases
        if " " in kw:
            # Multi-word phrase: substring match
            if kw in normalized:
                for idx in indices:
                    if book.entries[idx]["id"] not in exclude:
                        matched_indices.setdefault(idx, []).append(kw)
        else:
            # Single word: check as whole word to avoid false positives
            # e.g., "kin" shouldn't match "kinsweave" (kinsweave has its own entry)
            pattern = r"\b" + re.escape(kw) + r"\b"
            if re.search(pattern, normalized):
                for idx in indices:
                    if book.entries[idx]["id"] not in exclude:
                        matched_indices.setdefault(idx, []).append(kw)

    if not matched_indices:
        return []

    # Build result list sorted by priority (desc), then by number of keyword matches (desc)
    results = []
    for idx, keywords in matched_indices.items():
        entry = book.entries[idx]
        results.append({
            "id":               entry["id"],
            "content":          entry["content"],
            "priority":         entry["priority"],
            "max_tokens":       entry["max_tokens"],
            "matched_keywords": keywords,
        })

    results.sort(key=lambda e: (-e["priority"], -len(e["matched_keywords"])))

    # Cap by total token budget
    selected = []
    budget_remaining = max_total_tokens
    for entry in results:
        cost = entry["max_tokens"]
        if cost <= budget_remaining:
            selected.append(entry)
            budget_remaining -= cost
        elif budget_remaining <= 0:
            break

    return selected


# ---------------------------------------------------------------------------
# Prompt-injection helper
# ---------------------------------------------------------------------------

def build_lore_block(text: str, *,
                     max_total_tokens: int = DEFAULT_MAX_TOTAL_TOKENS,
                     exclude_ids: Optional[set] = None) -> Optional[str]:
    """Convenience: scan text for keywords and return a formatted prompt
    block, or None if nothing matched.

    Example output:
        WORLD LORE (relevant to this conversation):
        Aldenheim was a Vestri dwarf-hold where five druids...
        The Silence Breach opened in the southeastern foothills...
    """
    entries = scan_for_lore(text, max_total_tokens=max_total_tokens,
                            exclude_ids=exclude_ids)
    if not entries:
        return None

    parts = ["\nWORLD LORE (relevant to this conversation):"]
    for entry in entries:
        parts.append(entry["content"])
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Admin / debug
# ---------------------------------------------------------------------------

def lorebook_status() -> str:
    book = get_lorebook()
    n_entries = len(book.entries)
    n_keywords = len(book._keyword_index)
    total_tokens = sum(e.get("max_tokens", 0) for e in book.entries)
    return (f"Lorebook: {n_entries} entries, {n_keywords} unique keywords, "
            f"~{total_tokens} total tokens if all loaded")


def test_keyword(keyword: str) -> List[str]:
    """Return entry IDs that would trigger on a given keyword."""
    book = get_lorebook()
    kw = keyword.strip().lower()
    indices = book._keyword_index.get(kw, [])
    return [book.entries[i]["id"] for i in indices]
