"""
===============================================================================

Platform Showcase UI

===============================================================================

Responsible only for rendering.

No business logic.

No Observation logic.

No Measurement logic.

No Evidence logic.

===============================================================================
"""

from __future__ import annotations

import shutil
from typing import Any


# ============================================================================
# Terminal
# ============================================================================

WIDTH = shutil.get_terminal_size((120, 40)).columns


# ============================================================================
# ANSI Colors
# ============================================================================

class Color:

    RESET = "\033[0m"

    BOLD = "\033[1m"

    DIM = "\033[2m"

    RED = "\033[91m"

    GREEN = "\033[92m"

    YELLOW = "\033[93m"

    BLUE = "\033[94m"

    MAGENTA = "\033[95m"

    CYAN = "\033[96m"

    WHITE = "\033[97m"


def c(text: Any, color: str) -> str:
    return color + str(text) + Color.RESET


# ============================================================================
# Basic Layout
# ============================================================================

def line(char: str = "="):
    print(char * WIDTH)


def separator():
    print("-" * WIDTH)


def blank():
    print()


# ============================================================================
# Banner — shows the full canonical architecture
# ============================================================================

def banner():

    line()

    print(c("PIA LATENT ENGINE".center(WIDTH), Color.BOLD))

    print(c("COMPLETE PLATFORM SHOWCASE".center(WIDTH), Color.CYAN))

    line()

    print()

    print("Canonical Architecture")

    print()

    print(" GitHub")
    print("    |")
    print("    v")
    print(" Observation Layer")
    print("    |")
    print("    v")
    print(" Measurement Layer")
    print("    |")
    print("    v")
    print(" Evidence Layer")
    print("    |")
    print("    v")
    print(" Expertise Layer")
    print("    |")
    print("    v")
    print(" Knowledge Layer")
    print("    |")
    print("    v")
    print(c(" Organization Intelligence", Color.MAGENTA))
    print(c("    |  (Ownership . Coverage . Concentration . Bus Factor", Color.DIM))
    print(c("    |   Successor . Knowledge Risk . Health . Recommendations)", Color.DIM))
    print("    v")
    print(" Reasoning Layer")
    print("    |")
    print("    v")
    print(" Decision Layer")
    print("    |")
    print("    v")
    print(" Executive Intelligence Report")

    blank()

    line()


# ============================================================================
# Stage Header
# ============================================================================

def stage(index: int, total: int, title: str):

    blank()

    separator()

    print(c(f"[{index}/{total}] {title}", Color.CYAN))

    separator()


# ============================================================================
# Success / Warning / Error
# ============================================================================

def success(msg: str):
    print(c("[OK] " + msg, Color.GREEN))


def warning(msg: str):
    print(c("! " + msg, Color.YELLOW))


def error(msg: str):
    print(c("[ERR] " + msg, Color.RED))


# ============================================================================
# Metrics
# ============================================================================

def metric(name: str, value: Any):
    print(f"{name:<38} {value}")


# ============================================================================
# Section
# ============================================================================

def section(title: str):

    blank()

    print(c(title, Color.BOLD))


# ============================================================================
# Key / Value Table
# ============================================================================

def table(rows: list[tuple[str, Any]]):

    for key, value in rows:

        metric(key, value)


# ============================================================================
# Ranking
# ============================================================================

def ranking(title: str, values):

    section(title)

    if not values:

        print("  (empty)")

        return

    for idx, item in enumerate(values, start=1):

        print(f" {idx:>2}. {item}")


# ============================================================================
# Histogram
# ============================================================================

def histogram(title: str, histogram_data: dict):

    section(title)

    if not histogram_data:

        print("  (empty)")

        return

    maximum = max(histogram_data.values())

    for bucket in sorted(histogram_data):

        value = histogram_data[bucket]

        bar = "#" * int((value / maximum) * 40)

        print(f"{bucket:>6} | {bar} {value}")


# ============================================================================
# Progress Bar
# ============================================================================

def progress(title: str, current: int, total: int):

    if total <= 0:

        total = 1

    width = 40

    ratio = current / total

    filled = int(width * ratio)

    empty = width - filled

    print(
        f"{title:<20}"
        f"[{'#'*filled}{'.'*empty}] "
        f"{current}/{total}"
    )


# ============================================================================
# Dashboard Card
# ============================================================================

def card(title: str, rows: list[tuple[str, Any]]):

    separator()

    print(c(title, Color.BOLD))

    separator()

    table(rows)


# ============================================================================
# Final Summary
# ============================================================================

def summary(title: str, rows: list[tuple[str, Any]]):

    blank()

    line()

    print(c(title.center(WIDTH), Color.BOLD))

    line()

    table(rows)

    line()


# ============================================================================
# Lineage — traces canonical flow from Decision back to GitHub
# ============================================================================

def lineage(title: str):

    blank()

    section(title)

    print()

    print(" GitHub Commit")
    print("      |")
    print("      v")
    print(" Observation")
    print("      |")
    print("      v")
    print(" Measurement")
    print("      |")
    print("      v")
    print(" Evidence")
    print("      |")
    print("      v")
    print(" Expertise")
    print("      |")
    print("      v")
    print(" Knowledge")
    print("      |")
    print("      v")
    print(c(" Organization Intelligence", Color.MAGENTA))
    print("      |")
    print("      v")
    print(" Reasoning")
    print("      |")
    print("      v")
    print(" Decision")


# ============================================================================
# Future Layer Placeholder
# ============================================================================

def future_layer(name: str):

    separator()

    print(c(name, Color.MAGENTA))

    print()

    print(" Not Implemented Yet")

    separator()
