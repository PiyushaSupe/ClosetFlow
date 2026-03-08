"""
ClosetFlow Outfit Compatibility Engine

This module evaluates how well two clothing items match together.

Scoring Factors:
1. Color harmony
2. Pattern compatibility
3. Material compatibility
4. Style similarity
5. Category relationships

Total compatibility score is used by the recommendation engine.
"""

from itertools import combinations


# -----------------------------------------------------
# Color Harmony Rules
# -----------------------------------------------------

NEUTRAL_COLORS = {
    "white",
    "black",
    "grey",
    "navy",
    "beige"
}

COMPLEMENTARY_COLORS = {
    ("blue", "orange"),
    ("red", "green"),
    ("yellow", "purple")
}

ANALOGOUS_COLORS = {
    ("blue", "light_blue"),
    ("green", "olive"),
    ("red", "pink")
}


def color_score(c1, c2):
    """
    Evaluate color harmony between two clothing items.
    """

    if c1 == c2:
        return 10

    if c1 in NEUTRAL_COLORS or c2 in NEUTRAL_COLORS:
        return 8

    if (c1, c2) in COMPLEMENTARY_COLORS or (c2, c1) in COMPLEMENTARY_COLORS:
        return 9

    if (c1, c2) in ANALOGOUS_COLORS or (c2, c1) in ANALOGOUS_COLORS:
        return 7

    return 3


# -----------------------------------------------------
# Pattern Compatibility
# -----------------------------------------------------

def pattern_score(p1, p2):

    if p1 == "solid" and p2 == "solid":
        return 8

    if p1 == "solid" or p2 == "solid":
        return 7

    if p1 == p2:
        return 6

    return 3


# -----------------------------------------------------
# Material Compatibility
# -----------------------------------------------------

MATERIAL_MATCH = {
    ("cotton", "denim"),
    ("cotton", "cotton"),
    ("denim", "denim"),
    ("wool", "wool"),
    ("leather", "leather")
}


def material_score(m1, m2):

    if (m1, m2) in MATERIAL_MATCH or (m2, m1) in MATERIAL_MATCH:
        return 8

    if m1 == m2:
        return 7

    return 4


# -----------------------------------------------------
# Style Similarity
# -----------------------------------------------------

def style_score(tags1, tags2):

    if not tags1 or not tags2:
        return 3

    overlap = set(tags1).intersection(set(tags2))

    if len(overlap) >= 2:
        return 9

    if len(overlap) == 1:
        return 6

    return 2


# -----------------------------------------------------
# Category Logic
# -----------------------------------------------------

VALID_COMBINATIONS = {
    ("top", "bottom"),
    ("top", "outerwear"),
    ("outerwear", "top"),
    ("top", "footwear"),
    ("bottom", "footwear"),
    ("top", "accessory"),
    ("bottom", "accessory")
}


def category_score(cat1, cat2):

    if (cat1, cat2) in VALID_COMBINATIONS:
        return 7

    return 4


# -----------------------------------------------------
# Master Compatibility Function
# -----------------------------------------------------

def compatibility_score(item1, item2):
    """
    Calculate full compatibility score between two clothing items.
    """

    if not item1 or not item2:
        return 0

    score = 0

    # Color
    score += color_score(
        item1.get("color"),
        item2.get("color")
    )

    # Pattern
    score += pattern_score(
        item1.get("pattern"),
        item2.get("pattern")
    )

    # Material
    score += material_score(
        item1.get("material"),
        item2.get("material")
    )

    # Style
    score += style_score(
        item1.get("style_tags"),
        item2.get("style_tags")
    )

    # Category
    score += category_score(
        item1.get("category"),
        item2.get("category")
    )

    return score


# -----------------------------------------------------
# Full Outfit Compatibility
# -----------------------------------------------------

def outfit_score(items):
    """
    Evaluate compatibility across all items in an outfit.
    """

    if not items:
        return 0

    score = 0
    pairs = list(combinations(items, 2))

    for a, b in pairs:
        score += compatibility_score(a, b)

    return score