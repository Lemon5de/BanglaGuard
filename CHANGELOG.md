# Changelog

All notable changes to **BanglaGuard** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-11-15

### Added
- Per-server and per-channel moderation toggles (`/togglemoderation`) restricted to authorized staff (`@is_authed()`), supporting channel toggle, server-wide toggle, and read-only status inspection.
- Persistent per-guild configuration (`mod_config.json`) keyed by Guild ID (`str(guild.id)`) so server and channel moderation states persist across bot restarts.
- Dynamic `discord.Embed` status display switching between green (active) and red (paused) while listing all disabled channels.
- Detailed console audit logs in `contains_slur()` displaying raw input tokens, normalized/rebuilt forms, and matched slur entries.

### Fixed
- Cross-word boundary false positives by replacing global whitespace stripping with per-word tokenization (`raw.split()`), preventing adjacent harmless words (e.g., `"chat box"`) from merging.
- Double-consonant word collapsing by restricting repeated character deduplication to vowels (`[aeiou]`), protecting normal English words like `"ball"`.
- Short consonant skeleton over-matching by raising the minimum skeleton threshold from 3 to 4 characters and enforcing whole-word skeleton matching.

## [1.1.0] - 2026-10-22

### Added
- Category bypass filter (`IGNORED_CATEGORIES`) allowing staff, support, and information categories to skip slur moderation.
- Helper function `is_category_ignored()` supporting both category IDs and lowercased name string comparisons.

### Changed
- Refactored `on_message` listener to allow standard commands while bypassing moderation checks in ignored categories.

## [1.0.0] - 2026-10-21

### Added
- Core Bangla slur detection engine using custom character map translation, vowel stripping, and skeleton matching.
- Slash command system (`/addslur`, `/removeslur`, `/listslurs`, `/help`).
- Dynamic local storage persistence (`slurs.json`).
- Role-based and permission-based access control (`is_authed()` predicate).
- Auto-deletion of slur-containing messages with temporary warnings.