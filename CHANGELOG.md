# Changelog

All notable changes to **BanglaGuard** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-22

### Added
- Core Bangla slur detection engine using custom character map translation, vowel stripping, and skeleton matching.
- Slash command system (`/addslur`, `/removeslur`, `/listslurs`, `/help`).
- Dynamic local storage persistence (`slurs.json`).
- Role-based and permission-based access control (`is_authed()` predicate).
- Auto-deletion of slur-containing messages with temporary warnings.