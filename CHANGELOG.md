# Changelog

All notable changes to **BanglaGuard** will be documented in this file[cite: 37].

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)[cite: 37].

## [1.1.0] - 2026-10-22

### Added
- Category bypass filter (`IGNORED_CATEGORIES`) allowing staff, support, and information categories to skip slur moderation[cite: 34, 35, 36].
- Helper function `is_category_ignored()` supporting both category IDs and lowercased name string comparisons[cite: 35].

### Changed
- Refactored `on_message` listener to allow standard commands while bypassing moderation checks in ignored categories[cite: 36].

## [1.0.0] - 2026-10-21

### Added
- Core Bangla slur detection engine using custom character map translation, vowel stripping, and skeleton matching[cite: 37].
- Slash command system (`/addslur`, `/removeslur`, `/listslurs`, `/help`)[cite: 37].
- Dynamic local storage persistence (`slurs.json`)[cite: 37].
- Role-based and permission-based access control (`is_authed()` predicate)[cite: 37].
- Auto-deletion of slur-containing messages with temporary warnings[cite: 37].