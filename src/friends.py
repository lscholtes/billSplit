import re
from typing import List

import streamlit as st

from src.models import Friend


def parse_friends() -> List[Friend]:
    friends_str = st.text_area(
        label="friends_input",
        label_visibility="hidden",
        placeholder="Who would you like to split this bill with?",
    )
    friends = [
        Friend(name=name.strip())
        # Split list by commas and newlines
        for name in re.split("\n|,", friends_str)
    ]
    return friends
