"""
This file allow for more color maps.
"""

import typing

Colors = typing.List[str]

TRANSPARENT = "#ffffff00"

default: Colors = [
    TRANSPARENT,
    "firebrick",
    "lightcoral",
    "gainsboro",
    "cornflowerblue",
    "darkblue",
]

default_with_darker_neutral: Colors = [
    TRANSPARENT,
    "firebrick",
    "lightcoral",
    "silver",
    "cornflowerblue",
    "darkblue",
]

default_label_color = "white"

# default color scheme with neutral removed
likert4: Colors = list(default)
likert4.pop(len(likert4) // 2)

likert5: Colors = [TRANSPARENT, "#d8a539", "#efe0c1", "lightgray", "#bde1dd", "#5ab4ac"]

likert6: Colors = [
    TRANSPARENT,
    "#d8a539",
    "#dfc283",
    "#efe0c1",
    "#def0ee",
    "#7bc3bc",
    "#5ab4ac",
]
likert7: Colors = [
    TRANSPARENT,
    "#d8a539",
    "#dfc283",
    "#efe0c1",
    "lightgray",
    "#bde1dd",
    "#7bc3bc",
    "#5ab4ac",
]

likert8: Colors = [
    TRANSPARENT,
    "#d8b365",
    "#dfc283",
    "#e7d1a2",
    "#efe0c1",
    "#bde1dd",
    "#9cd2cd",
    "#7bc3bc",
    "#5ab4ac",
]

likert9: Colors = [
    TRANSPARENT,
    "#d8b365",
    "#dfc283",
    "#e7d1a2",
    "#efe0c1",
    "lightgray",
    "#bde1dd",
    "#9cd2cd",
    "#7bc3bc",
    "#5ab4ac",
]

likert10: Colors = [
    TRANSPARENT,
    "#d8b365",
    "#dfc283",
    "#e7d1a2",
    "#efe0c1",
    "#f7efe0",
    "#def0ee",
    "#bde1dd",
    "#9cd2cd",
    "#7bc3bc",
    "#5ab4ac",
]
