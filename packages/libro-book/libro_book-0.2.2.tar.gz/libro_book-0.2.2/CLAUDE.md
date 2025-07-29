# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Libro is a command-line tool for tracking personal reading history. It stores book and review data in a local SQLite database and provides various reporting and display features. The application is built with Python 3.10+ and uses Rich for terminal formatting.

## Commands

### Development Commands
- `just install` - Install dependencies using uv
- `just lint` - Run ruff linting on src/libro/
- `just clean` - Remove build artifacts and Python cache files
- `just build` - Clean, lint, install, and build the package
- `just run <args>` - Run the CLI application with arguments
- `uv run libro <args>` - Alternative way to run the application

### Testing and Quality
- `ruff check src/libro/` - Lint the codebase (configured in pyproject.toml)

### Build and Release
- `just publish` - Build and publish to PyPI as `libro-book`
- `py -m build` - Build the package
- `py -m twine upload dist/*` - Upload to PyPI

## Architecture

### Core Structure
- `src/libro/main.py` - Entry point with CLI argument parsing and command routing
- `src/libro/models.py` - Data classes for Book, Review, and BookReview
- `src/libro/config.py` - Configuration and argument parsing
- `src/libro/actions/` - Command implementations:
  - `db.py` - Database initialization
  - `show.py` - Display books and reviews
  - `report.py` - Generate reading reports and statistics
  - `modify.py` - Add and edit books/reviews
  - `importer.py` - Import from external sources (Goodreads)

### Database Schema
- `books` table: id, title, author, pages, pub_year, genre
- `reviews` table: id, book_id (FK), date_read, rating, review

### Key Design Patterns
- Uses dataclasses for clean data modeling
- SQLite with row factory for named column access
- Command pattern for CLI actions
- Rich library for terminal formatting and tables

### Database Location Priority
1. `--db` command-line flag
2. `libro.db` in current directory
3. `LIBRO_DB` environment variable
4. Platform-specific data directory

### Package Management
- Uses `uv` for dependency management and virtual environments
- Built with `hatchling` build system
- Published to PyPI as `libro-book` (not `libro` due to naming conflicts)
- Configured for Python 3.10+ compatibility

### Data Sources
The `/data/` directory contains JSON files with book metadata for fiction and nonfiction books, used for testing or seeding data. Ignore the `/data/` directory.