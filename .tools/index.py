#!/usr/bin/env python3
"""Vault Index DB — structural memory for the knowledge vault.

Commands:
  rebuild       Delete and rebuild .index.db from scratch
  reconcile     Detect ghosts, unindexed, and stale entries
  stats         Summary counts by type, confidence, freshness
  stale [days]  List entities not verified within N days (default 30)
  query <sql>   Execute raw SQL and print results
  deps <id>     Show outbound and inbound dependencies for an entity
  cascade <id>  Trace downstream cascade (depth 3) from an entity
  index-intel   Parse changelog/patterns/ideas into intelligence table
  intel         Query intelligence table with filters
"""

import sys
import os
import re
import json
import sqlite3
import glob
import argparse
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip3 install pyyaml", file=sys.stderr)
    sys.exit(1)

VAULT_ROOT = Path(__file__).resolve().parent.parent  # .tools/ -> vault root
DB_PATH = VAULT_ROOT / ".index.db"
SCHEMA_PATH = VAULT_ROOT / ".tools" / "schema.sql"
ENTITY_TYPES = {"competitor", "content", "partner", "research", "decision"}
BASE_FIELDS = {
    "type", "name", "status", "source", "last_verified", "confidence",
    "verified_by", "created_at", "updated_at",
}

# Dirs to skip when walking vault
SKIP_DIRS = {"_templates"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def path_to_id(vault_path: str) -> str:
    """Strip vault root prefix and .md extension.

    'competitors/acme-corp.md' → 'competitors/acme-corp'
    """
    p = vault_path
    if p.endswith(".md"):
        p = p[:-3]
    return p


def parse_note(abs_path: Path, vault_root: Path) -> dict:
    """Parse a vault note into frontmatter, body, wikilinks, and vault_path.

    Returns a dict with keys:
      frontmatter (dict), body (str), wikilinks (list[str]), vault_path (str)

    On YAML parse errors or missing frontmatter, returns frontmatter={}.
    """
    vault_path = str(abs_path.relative_to(vault_root))
    result = {
        "frontmatter": {},
        "body": "",
        "wikilinks": [],
        "vault_path": vault_path,
    }

    try:
        text = abs_path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        print(f"  WARN: cannot read {vault_path}: {e}", file=sys.stderr)
        return result

    # Extract YAML frontmatter delimited by ---
    fm_match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?", text, re.DOTALL)
    if fm_match:
        fm_text = fm_match.group(1)
        body = text[fm_match.end():]
        try:
            fm = yaml.safe_load(fm_text) or {}
            if not isinstance(fm, dict):
                fm = {}
        except yaml.YAMLError as e:
            print(f"  WARN: YAML error in {vault_path}: {e}", file=sys.stderr)
            fm = {}
        result["frontmatter"] = fm
        result["body"] = body
    else:
        result["body"] = text

    # Extract wikilinks from full text: [[target]] or [[target|alias]] or [[target#heading]]
    raw_links = re.findall(r"\[\[([^\]|#]+)", text)
    result["wikilinks"] = [lnk.strip() for lnk in raw_links if lnk.strip()]

    return result


def build_entity(fm: dict, vault_path: str, now: str) -> dict:
    """Build an entity row dict from frontmatter and vault path."""
    stem = Path(vault_path).stem  # filename without .md
    stem_name = stem.replace("-", " ").replace("_", " ").title()

    name = fm.get("name") or fm.get("title") or stem_name

    # Gather non-base fields into meta JSON
    meta_fields = {k: v for k, v in fm.items() if k not in BASE_FIELDS}
    meta = json.dumps(meta_fields, default=str) if meta_fields else None

    # Coerce dates/values to strings for SQLite
    def to_str(v):
        if v is None:
            return None
        if isinstance(v, (datetime,)):
            return v.isoformat()
        return str(v)

    return {
        "id": path_to_id(vault_path),
        "type": to_str(fm.get("type")),
        "vault_path": vault_path,
        "name": to_str(name),
        "status": to_str(fm.get("status", "active")),
        "created_at": to_str(fm.get("created_at")),
        "updated_at": to_str(fm.get("updated_at", now)),
        "last_verified": to_str(fm.get("last_verified")),
        "verified_by": to_str(fm.get("verified_by")),
        "confidence": to_str(fm.get("confidence", "estimated")),
        "meta": meta,
    }


def get_connection(path: Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def apply_schema(conn: sqlite3.Connection) -> None:
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    conn.executescript(schema)
    conn.commit()


def walk_vault(vault_root: Path):
    """Yield all .md file paths in vault, skipping hidden dirs and _templates."""
    for root, dirs, files in os.walk(str(vault_root)):
        root_path = Path(root)
        # Skip hidden directories (starting with .) and SKIP_DIRS
        dirs[:] = [
            d for d in dirs
            if not d.startswith(".") and d not in SKIP_DIRS
        ]
        for fname in files:
            if fname.endswith(".md"):
                yield root_path / fname


# ---------------------------------------------------------------------------
# Dependency Discovery (Phase 4)
# ---------------------------------------------------------------------------

def discover_dependencies(conn: sqlite3.Connection, now: str) -> int:
    """Discover dependencies from wikilinks and explicit references."""
    # Build entity ID lookup
    entity_ids = set()
    stem_to_id = {}
    for row in conn.execute("SELECT id FROM entities"):
        eid = row["id"]
        entity_ids.add(eid)
        stem = eid.rsplit('/', 1)[-1] if '/' in eid else eid
        stem_to_id[stem] = eid

    dep_count = 0
    for abs_path in walk_vault(VAULT_ROOT):
        parsed = parse_note(abs_path, VAULT_ROOT)
        fm = parsed["frontmatter"]
        etype = str(fm.get("type", "")).lower()
        source_id = path_to_id(parsed["vault_path"])

        # Only track deps FROM entity notes
        if etype not in ENTITY_TYPES:
            continue

        # Explicit references from frontmatter
        refs = fm.get("references", [])
        if isinstance(refs, list):
            for ref in refs:
                ref_str = str(ref)
                target = ref_str if ref_str in entity_ids else stem_to_id.get(ref_str)
                if target and target != source_id:
                    try:
                        conn.execute(
                            """INSERT OR REPLACE INTO dependencies
                               (source_id, target_id, relationship, discovered_at)
                               VALUES (?, ?, 'explicit', ?)""",
                            (source_id, target, now),
                        )
                        dep_count += 1
                    except sqlite3.Error:
                        pass

        # Wikilinks from body
        for link in parsed["wikilinks"]:
            link = link.strip().strip("/")
            target = None
            if link in entity_ids:
                target = link
            else:
                slug = link.replace(" ", "-").lower()
                if slug in entity_ids:
                    target = slug
                else:
                    stem = link.rsplit("/", 1)[-1] if "/" in link else link
                    stem_lower = stem.replace(" ", "-").lower()
                    target = stem_to_id.get(stem_lower) or stem_to_id.get(stem)

            if target and target != source_id:
                try:
                    conn.execute(
                        """INSERT OR REPLACE INTO dependencies
                           (source_id, target_id, relationship, discovered_at)
                           VALUES (?, ?, 'wikilink', ?)""",
                        (source_id, target, now),
                    )
                    dep_count += 1
                except sqlite3.Error:
                    pass

    return dep_count


# ---------------------------------------------------------------------------
# Intelligence Parsers (Phase 5)
# ---------------------------------------------------------------------------

def build_entity_name_lookup(conn: sqlite3.Connection) -> dict:
    """Build name→id lookup for entity resolution."""
    lookup = {}
    for row in conn.execute("SELECT id, name FROM entities"):
        eid, name = row["id"], row["name"]
        if name:
            lookup[name.lower()] = eid
            stem = eid.rsplit("/", 1)[-1] if "/" in eid else eid
            lookup[stem.replace("-", " ")] = eid
    return lookup


def resolve_entity(name: str, lookup: dict):
    """Try to resolve a name to an entity ID."""
    if not name:
        return None
    name_lower = name.lower().strip()
    # Exact match
    if name_lower in lookup:
        return lookup[name_lower]
    # Suffix expansion for common business name patterns
    for suffix in [" services", " cleaning", " solutions", " pro", " group",
                   " co", " inc", " llc", " ltd", " consulting", " studio"]:
        if name_lower + suffix in lookup:
            return lookup[name_lower + suffix]
    # Slug match against entity IDs directly
    slug = name_lower.replace(" ", "-")
    for prefix in ["competitors/", "partners/", "content/", "research/"]:
        candidate = prefix + slug
        for v in lookup.values():
            if v == candidate:
                return v
    # Prefix match: "Acme Design" should match "Acme Design & Build"
    # Only match if the query is 2+ words (avoid false positives from single words)
    if " " in name_lower:
        best = None
        for k, v in lookup.items():
            if k.startswith(name_lower) and (best is None or len(k) < len(best[0])):
                best = (k, v)
        if best:
            return best[1]
    return None


def parse_changelog(path: str, entity_lookup: dict) -> list[dict]:
    """Parse intelligence changelog entries."""
    entries = []
    if not os.path.exists(path):
        return entries

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        # TIER CHANGE
        m = re.match(r"^\[(\d{4}-\d{2}-\d{2})\]\s+TIER CHANGE:\s+(.+)$", line)
        if m:
            date, rest = m.group(1), m.group(2)
            name_m = re.match(r"^(.+?)\s+T\d", rest)
            comp_name = name_m.group(1) if name_m else None
            entity_id = resolve_entity(comp_name, entity_lookup) if comp_name else None
            entries.append({
                "type": "changelog", "date": date, "entity_id": entity_id,
                "vector": "TIER_CHANGE", "content": rest.strip(),
                "signal": "YES", "importance": "critical",
                "status": "active", "source_file": "intelligence/changelog.md",
            })
            i += 1
            continue

        # NEW TARGET
        m = re.match(r"^\[(\d{4}-\d{2}-\d{2})\]\s+NEW TARGET:\s+(.+)$", line)
        if m:
            date, rest = m.group(1), m.group(2)
            name_m = re.match(r"^(\w[\w\s]+?)\s+added", rest)
            comp_name = name_m.group(1) if name_m else None
            entity_id = resolve_entity(comp_name, entity_lookup) if comp_name else None
            entries.append({
                "type": "changelog", "date": date, "entity_id": entity_id,
                "vector": "NEW_TARGET", "content": rest.strip(),
                "signal": "YES", "importance": "critical",
                "status": "active", "source_file": "intelligence/changelog.md",
            })
            i += 1
            continue

        # Category-level: [DATE] [CATEGORY] [SUBCATEGORY]: description (no entity)
        m = re.match(r"^\[(\d{4}-\d{2}-\d{2})\]\s+\[([A-Z_ ]+)\]\s+\[([A-Z_ ]+)\]:\s+(.+)$", line)
        if m:
            date, category, subcategory, content = m.group(1), m.group(2).strip(), m.group(3).strip(), m.group(4)
            vector = f"{category}/{subcategory}"

            signal = None
            importance = "normal"
            i += 1
            while i < len(lines) and lines[i].startswith("  "):
                sig_m = re.match(r"^\s+Signal:\s+(YES|NO)", lines[i])
                if sig_m:
                    signal = sig_m.group(1)
                    if signal == "YES":
                        importance = "critical"
                else:
                    content += " " + lines[i].strip()
                i += 1

            entries.append({
                "type": "changelog", "date": date, "entity_id": None,
                "vector": vector, "content": content.strip(),
                "signal": signal, "importance": importance,
                "status": "active", "source_file": "intelligence/changelog.md",
            })
            continue

        # Standard: [DATE] NAME [VECTOR]: description
        m = re.match(r"^\[(\d{4}-\d{2}-\d{2})\]\s+(.+?)\s+\[([A-Z_]+)\]:\s+(.+)$", line)
        if m:
            date, comp_name, vector, content = m.group(1), m.group(2), m.group(3), m.group(4)
            entity_id = resolve_entity(comp_name, entity_lookup)

            signal = None
            importance = "normal"
            i += 1
            while i < len(lines) and lines[i].startswith("  "):
                sig_m = re.match(r"^\s+Signal:\s+(YES|NO)", lines[i])
                if sig_m:
                    signal = sig_m.group(1)
                    if signal == "YES":
                        importance = "critical"
                else:
                    content += " " + lines[i].strip()
                i += 1

            entries.append({
                "type": "changelog", "date": date, "entity_id": entity_id,
                "vector": vector, "content": content.strip(),
                "signal": signal, "importance": importance,
                "status": "active", "source_file": "intelligence/changelog.md",
            })
            continue

        i += 1

    return entries


def parse_patterns(path: str) -> list[dict]:
    """Parse intelligence patterns entries."""
    entries = []
    if not os.path.exists(path):
        return entries

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        line = line.rstrip()
        m = re.match(r"^\[(\d{4}-\d{2}-\d{2})\]\s+(\w+!?):\s+(.+)$", line)
        if m:
            date, category, content = m.group(1), m.group(2), m.group(3)
            importance = "critical" if category.endswith("!") else "normal"
            category_clean = category.rstrip("!")
            entries.append({
                "type": "pattern", "date": date, "entity_id": None,
                "vector": category_clean, "content": content.strip(),
                "signal": None, "importance": importance,
                "status": "active", "source_file": "intelligence/patterns.md",
            })

    return entries


def parse_ideas(path: str, entity_lookup: dict) -> list[dict]:
    """Parse ideas-board entries (multi-line blocks)."""
    entries = []
    if not os.path.exists(path):
        return entries

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    blocks = re.split(r"(?=\[\d{4}-\d{2}-\d{2}\]\s+IDEA:)", text)

    for block in blocks:
        block = block.strip()
        m = re.match(r"^\[(\d{4}-\d{2}-\d{2})\]\s+IDEA:\s+(.+)", block)
        if not m:
            continue

        date, idea_name = m.group(1), m.group(2).strip()

        fields = {}
        for field_m in re.finditer(
            r"^\s+(Source|How|Our version|Effort|Impact|Status|Related):\s+(.+?)(?=\n\s+\w+:|$)",
            block, re.MULTILINE | re.DOTALL,
        ):
            fields[field_m.group(1)] = field_m.group(2).strip()

        entity_id = None
        source = fields.get("Source", "")
        source_links = re.findall(r"\[\[(?:competitors/|partners/)?([^\]|#]+)", source)
        if source_links:
            entity_id = resolve_entity(source_links[0], entity_lookup)

        effort = fields.get("Effort", "PROJECT")
        impact = fields.get("Impact", "MEDIUM").lower()
        status_raw = fields.get("Status", "NEW").upper()

        how = fields.get("How", "")
        our_version = fields.get("Our version", "")
        content = f"{idea_name} | {how} | {our_version}".strip(" |")

        entries.append({
            "type": "idea", "date": date, "entity_id": entity_id,
            "vector": effort, "content": content,
            "signal": status_raw, "importance": impact,
            "status": "rejected" if status_raw == "REJECTED" else "active",
            "source_file": "intelligence/ideas-board.md",
        })

    return entries


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_rebuild() -> None:
    """Delete .index.db and rebuild from scratch."""
    print("=== Rebuild ===")
    if DB_PATH.exists():
        DB_PATH.unlink()
        print(f"  Deleted existing {DB_PATH}")

    conn = get_connection()
    apply_schema(conn)
    print(f"  Schema applied from {SCHEMA_PATH}")

    now = now_iso()
    type_counts: dict[str, int] = {}
    total_scanned = 0
    total_indexed = 0
    parse_errors = 0

    entity_rows = []
    provenance_rows = []

    for abs_path in walk_vault(VAULT_ROOT):
        total_scanned += 1
        parsed = parse_note(abs_path, VAULT_ROOT)
        fm = parsed["frontmatter"]

        if not fm:
            # File without frontmatter — not indexable
            continue

        entity_type = fm.get("type")
        if entity_type not in ENTITY_TYPES:
            continue

        try:
            row = build_entity(fm, parsed["vault_path"], now)
        except Exception as e:
            print(f"  ERROR building entity for {parsed['vault_path']}: {e}", file=sys.stderr)
            parse_errors += 1
            continue

        entity_rows.append(row)
        provenance_rows.append({
            "entity_id": row["id"],
            "action": "rebuild",
            "performed_by": "index.py",
            "performed_at": now,
            "details": f"Initial index from {parsed['vault_path']}",
        })
        type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
        total_indexed += 1

    # Bulk insert
    conn.executemany(
        """INSERT OR REPLACE INTO entities
           (id, type, vault_path, name, status, created_at, updated_at,
            last_verified, verified_by, confidence, meta)
           VALUES (:id, :type, :vault_path, :name, :status, :created_at, :updated_at,
                   :last_verified, :verified_by, :confidence, :meta)""",
        entity_rows,
    )
    conn.executemany(
        """INSERT INTO provenance (entity_id, action, performed_by, performed_at, details)
           VALUES (:entity_id, :action, :performed_by, :performed_at, :details)""",
        provenance_rows,
    )
    conn.commit()

    # Discover dependencies from wikilinks + explicit references
    dep_count = discover_dependencies(conn, now)
    conn.commit()
    conn.close()

    print(f"\n  Results:")
    print(f"    Files scanned:  {total_scanned}")
    print(f"    Entities indexed: {total_indexed}")
    print(f"    Dependencies:   {dep_count}")
    print(f"    Parse errors:   {parse_errors}")
    print(f"\n  By type:")
    for t in sorted(type_counts):
        print(f"    {t:<20} {type_counts[t]}")
    print(f"\n  DB written to: {DB_PATH}")


def cmd_reconcile() -> None:
    """Report ghosts, unindexed entities, and stale entries."""
    print("=== Reconcile ===")

    if not DB_PATH.exists():
        print("  ERROR: .index.db not found. Run 'rebuild' first.")
        sys.exit(1)

    conn = get_connection()
    now = now_iso()

    # Paths currently in DB
    db_rows = conn.execute("SELECT id, vault_path, updated_at FROM entities").fetchall()
    db_by_path = {row["vault_path"]: row for row in db_rows}

    # Paths currently in vault with entity frontmatter
    vault_entity_paths: dict[str, Path] = {}
    for abs_path in walk_vault(VAULT_ROOT):
        parsed = parse_note(abs_path, VAULT_ROOT)
        if parsed["frontmatter"].get("type") in ENTITY_TYPES:
            vault_entity_paths[parsed["vault_path"]] = abs_path

    db_paths = set(db_by_path.keys())
    vault_paths = set(vault_entity_paths.keys())

    ghosts = db_paths - vault_paths           # In DB but missing from vault
    unindexed = vault_paths - db_paths        # In vault but not in DB
    common = db_paths & vault_paths

    # Stale: file mtime newer than DB updated_at
    stale = []
    for vpath in common:
        abs_path = vault_entity_paths[vpath]
        try:
            mtime = datetime.fromtimestamp(abs_path.stat().st_mtime, tz=timezone.utc)
            mtime_str = mtime.strftime("%Y-%m-%dT%H:%M:%SZ")
            db_updated = db_by_path[vpath]["updated_at"] or ""
            if mtime_str > db_updated:
                stale.append((vpath, mtime_str, db_updated))
        except OSError:
            pass

    conn.close()

    print(f"\n  Ghosts (in DB, file missing): {len(ghosts)}")
    for p in sorted(ghosts):
        print(f"    - {p}")

    print(f"\n  Unindexed (in vault, not in DB): {len(unindexed)}")
    for p in sorted(unindexed):
        print(f"    + {p}")

    print(f"\n  Stale (file modified after last index): {len(stale)}")
    for vpath, mtime, db_upd in sorted(stale)[:20]:
        print(f"    ~ {vpath}")
        print(f"        file mtime: {mtime}  |  db updated_at: {db_upd or 'none'}")
    if len(stale) > 20:
        print(f"    ... and {len(stale) - 20} more")

    print(f"\n  Summary: {len(ghosts)} ghosts | {len(unindexed)} unindexed | {len(stale)} stale")


def cmd_stats() -> None:
    """Print summary statistics from the index DB."""
    print("=== Stats ===")

    if not DB_PATH.exists():
        print("  ERROR: .index.db not found. Run 'rebuild' first.")
        sys.exit(1)

    conn = get_connection()

    print("\n  Entities by type:")
    for row in conn.execute("SELECT type, COUNT(*) as n FROM entities GROUP BY type ORDER BY n DESC"):
        print(f"    {row['type']:<24} {row['n']}")

    print("\n  Entities by confidence:")
    for row in conn.execute("SELECT confidence, COUNT(*) as n FROM entities GROUP BY confidence ORDER BY n DESC"):
        print(f"    {(row['confidence'] or 'null'):<24} {row['n']}")

    null_verified = conn.execute(
        "SELECT COUNT(*) as n FROM entities WHERE last_verified IS NULL"
    ).fetchone()["n"]
    print(f"\n  Never verified:              {null_verified}")

    stale_30 = conn.execute(
        "SELECT COUNT(*) as n FROM entities WHERE last_verified IS NULL OR last_verified < date('now', '-30 days')"
    ).fetchone()["n"]
    print(f"  Stale (>30 days or never):   {stale_30}")

    dep_count = conn.execute("SELECT COUNT(*) as n FROM dependencies").fetchone()["n"]
    print(f"\n  Dependencies:                {dep_count}")

    intel_count = conn.execute("SELECT COUNT(*) as n FROM intelligence").fetchone()["n"]
    print(f"  Intelligence entries:        {intel_count}")

    total = conn.execute("SELECT COUNT(*) as n FROM entities").fetchone()["n"]
    print(f"\n  Total entities:              {total}")

    conn.close()


def cmd_stale(days: int = 30) -> None:
    """List entities not verified within N days (or never verified)."""
    print(f"=== Stale Entities (>{days} days) ===")

    if not DB_PATH.exists():
        print("  ERROR: .index.db not found. Run 'rebuild' first.")
        sys.exit(1)

    conn = get_connection()
    rows = conn.execute(
        """SELECT id, type, name, last_verified FROM entities
           WHERE last_verified IS NULL OR last_verified < date('now', '-' || ? || ' days')
           ORDER BY type, last_verified""",
        (str(days),),
    ).fetchall()
    conn.close()

    if not rows:
        print(f"  No entities stale beyond {days} days.")
        return

    current_type = None
    for row in rows:
        if row["type"] != current_type:
            current_type = row["type"]
            print(f"\n  [{current_type}]")
        verified = row["last_verified"] or "never"
        print(f"    {row['id']:<50}  verified: {verified}")

    print(f"\n  Total: {len(rows)}")


def cmd_query(sql: str) -> None:
    """Execute raw SQL against the index DB and print results."""
    if not DB_PATH.exists():
        print("  ERROR: .index.db not found. Run 'rebuild' first.")
        sys.exit(1)

    conn = get_connection()
    try:
        cursor = conn.execute(sql)
        rows = cursor.fetchall()
        if not rows:
            print("  (no results)")
            return

        # Print header
        cols = [d[0] for d in cursor.description]
        col_widths = [max(len(c), max((len(str(r[c])) for r in rows), default=0)) for c in cols]
        header = "  " + "  ".join(str(c).ljust(w) for c, w in zip(cols, col_widths))
        print(header)
        print("  " + "  ".join("-" * w for w in col_widths))
        for row in rows:
            print("  " + "  ".join(str(row[c]).ljust(w) for c, w in zip(cols, col_widths)))
        print(f"\n  ({len(rows)} row{'s' if len(rows) != 1 else ''})")
    except sqlite3.Error as e:
        print(f"  SQL error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        conn.close()


def cmd_deps(entity_id: str) -> None:
    """Show outbound and inbound dependencies for an entity."""
    print(f"=== Dependencies: {entity_id} ===")

    if not DB_PATH.exists():
        print("  ERROR: .index.db not found. Run 'rebuild' first.")
        sys.exit(1)

    conn = get_connection()

    outbound = conn.execute(
        "SELECT target_id, relationship, field, context FROM dependencies WHERE source_id = ?",
        (entity_id,),
    ).fetchall()

    inbound = conn.execute(
        "SELECT source_id, relationship, field, context FROM dependencies WHERE target_id = ?",
        (entity_id,),
    ).fetchall()

    conn.close()

    print(f"\n  References ({len(outbound)}):")
    if outbound:
        for row in outbound:
            line = f"    → {row['target_id']}  [{row['relationship']}]"
            if row["field"]:
                line += f"  field={row['field']}"
            print(line)
    else:
        print("    (none)")

    print(f"\n  Referenced by ({len(inbound)}):")
    if inbound:
        for row in inbound:
            line = f"    ← {row['source_id']}  [{row['relationship']}]"
            if row["field"]:
                line += f"  field={row['field']}"
            print(line)
    else:
        print("    (none)")


def cmd_cascade(entity_id: str) -> None:
    """What breaks if this entity changes? Traces inbound references recursively."""
    print(f"=== Cascade Impact: {entity_id} ===")

    if not DB_PATH.exists():
        print("  ERROR: .index.db not found. Run 'rebuild' first.")
        sys.exit(1)

    conn = get_connection()
    rows = conn.execute(
        """WITH RECURSIVE cascade AS (
             SELECT source_id AS affected, 1 AS depth
             FROM dependencies WHERE target_id = ?
             UNION ALL
             SELECT d.source_id, c.depth + 1
             FROM dependencies d
             JOIN cascade c ON d.target_id = c.affected
             WHERE c.depth < 3
           )
           SELECT DISTINCT affected, MIN(depth) AS depth
           FROM cascade
           GROUP BY affected
           ORDER BY depth, affected""",
        (entity_id,),
    ).fetchall()
    conn.close()

    if not rows:
        print("\n  No upstream dependents found.")
        return

    print(f"\n  Entities that depend on {entity_id} (depth <= 3):")
    current_depth = None
    for row in rows:
        if row["depth"] != current_depth:
            current_depth = row["depth"]
            print(f"\n  Depth {current_depth}:")
        print(f"    {row['affected']}")

    print(f"\n  Total affected: {len(rows)}")


def cmd_index_intel() -> None:
    """Parse changelog, patterns, ideas-board into intelligence table."""
    print("=== Index Intelligence ===")

    if not DB_PATH.exists():
        print("  ERROR: .index.db not found. Run 'rebuild' first.")
        sys.exit(1)

    conn = get_connection()
    entity_lookup = build_entity_name_lookup(conn)

    changelog_path = str(VAULT_ROOT / "intelligence" / "changelog.md")
    patterns_path = str(VAULT_ROOT / "intelligence" / "patterns.md")
    ideas_path = str(VAULT_ROOT / "intelligence" / "ideas-board.md")

    changelog = parse_changelog(changelog_path, entity_lookup)
    patterns = parse_patterns(patterns_path)
    ideas = parse_ideas(ideas_path, entity_lookup)

    all_entries = changelog + patterns + ideas

    # Dedup: check (type, date, content[:100]) before inserting
    existing = set()
    for row in conn.execute("SELECT type, date, substr(content, 1, 100) FROM intelligence"):
        existing.add((row[0], row[1], row[2]))

    inserted = {"changelog": 0, "pattern": 0, "idea": 0}
    skipped = 0
    for entry in all_entries:
        key = (entry["type"], entry["date"], entry["content"][:100])
        if key in existing:
            skipped += 1
            continue
        existing.add(key)

        conn.execute(
            """INSERT INTO intelligence (type, date, entity_id, vector, content, signal,
               importance, status, source_file)
               VALUES (:type, :date, :entity_id, :vector, :content, :signal,
               :importance, :status, :source_file)""",
            entry,
        )
        inserted[entry["type"]] = inserted.get(entry["type"], 0) + 1

    conn.commit()
    conn.close()

    total = sum(inserted.values())
    print(f"\n  Changelog: {inserted.get('changelog', 0)} new")
    print(f"  Patterns:  {inserted.get('pattern', 0)} new")
    print(f"  Ideas:     {inserted.get('idea', 0)} new")
    print(f"  Skipped:   {skipped} (already indexed)")
    print(f"  Total new: {total}")


def cmd_intel(argv: list[str]) -> None:
    """Query intelligence table with filters."""
    if not DB_PATH.exists():
        print("  ERROR: .index.db not found. Run 'rebuild' first.")
        sys.exit(1)

    parser = argparse.ArgumentParser(prog="index.py intel")
    parser.add_argument("--type", choices=["changelog", "pattern", "idea"])
    parser.add_argument("--entity")
    parser.add_argument("--days", type=int)
    parser.add_argument("--signal-only", action="store_true")
    parser.add_argument("--importance", choices=["critical", "normal"])
    parser.add_argument("--status")
    args = parser.parse_args(argv)

    conn = get_connection()

    conditions = ["1=1"]
    params = []

    if args.type:
        conditions.append("type = ?")
        params.append(args.type)
    if args.entity:
        conditions.append("entity_id = ?")
        params.append(args.entity)
    if args.days:
        conditions.append("date >= date('now', '-' || ? || ' days')")
        params.append(str(args.days))
    if args.signal_only:
        conditions.append("signal = 'YES'")
    if args.importance:
        conditions.append("importance = ?")
        params.append(args.importance)
    if args.status:
        conditions.append("signal = ?")
        params.append(args.status)

    where = " AND ".join(conditions)
    sql = f"""SELECT date, type, entity_id, vector, content, signal, importance
              FROM intelligence WHERE {where}
              ORDER BY date DESC LIMIT 50"""

    rows = conn.execute(sql, params).fetchall()
    conn.close()

    print(f"Intelligence query ({len(rows)} results):\n")
    for row in rows:
        ent_str = f" [{row['entity_id']}]" if row["entity_id"] else ""
        sig_str = f" Signal:{row['signal']}" if row["signal"] else ""
        imp_str = " !" if row["importance"] == "critical" else ""
        print(f"  [{row['date']}] {row['type'].upper()}{ent_str} ({row['vector']}){imp_str}{sig_str}")
        content = row["content"]
        if len(content) > 120:
            print(f"    {content[:120]}...")
        else:
            print(f"    {content}")
        print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

USAGE = """Usage: index.py <command> [args]

Commands:
  rebuild             Delete and rebuild .index.db from vault
  reconcile           Detect ghosts, unindexed, and stale entries
  stats               Summary counts by type, confidence, freshness
  stale [days]        List entities not verified in N days (default 30)
  query "<sql>"       Execute raw SQL and print results
  deps <entity-id>    Show outbound and inbound dependencies
  cascade <entity-id> What breaks if this entity changes (depth 3)
  index-intel         Parse changelog/patterns/ideas into intelligence table
  intel [flags]       Query intelligence (--type, --entity, --days, --signal-only, --importance, --status)
"""

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(USAGE)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "rebuild":
        cmd_rebuild()
    elif cmd == "reconcile":
        cmd_reconcile()
    elif cmd == "stats":
        cmd_stats()
    elif cmd == "stale":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        cmd_stale(days)
    elif cmd == "query":
        if len(sys.argv) < 3:
            print("  Usage: index.py query \"<sql>\"")
            sys.exit(1)
        cmd_query(sys.argv[2])
    elif cmd == "deps":
        if len(sys.argv) < 3:
            print("  Usage: index.py deps <entity-id>")
            sys.exit(1)
        cmd_deps(sys.argv[2])
    elif cmd == "cascade":
        if len(sys.argv) < 3:
            print("  Usage: index.py cascade <entity-id>")
            sys.exit(1)
        cmd_cascade(sys.argv[2])
    elif cmd == "index-intel":
        cmd_index_intel()
    elif cmd == "intel":
        cmd_intel(sys.argv[2:])
    else:
        print(f"Unknown command: {cmd}")
        print(USAGE)
        sys.exit(1)
