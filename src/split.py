from dataclasses import dataclass
from typing import List

import streamlit as st

from src.models import Friend, LineEntry, Receipt


@dataclass
class ColumnSpec:
    name: str
    width: int


SPLIT_COLUMNS = [
    ColumnSpec(name="Item", width=3),
    ColumnSpec(name="Claimants", width=2),
    ColumnSpec(name="Uneven split?", width=1),
]


def get_column_widths() -> List[int]:
    return [c.width for c in SPLIT_COLUMNS]


def get_column_names() -> List[str]:
    return [c.name for c in SPLIT_COLUMNS]


def create_line_entry(entry: LineEntry, friends: List[Friend]) -> None:

    columns = dict(zip(get_column_names(), st.columns(get_column_widths())))

    with columns["Item"]:
        st.markdown(f"{entry.item_name} | **£{entry.item_cost:.2f}**")

    with columns["Claimants"]:
        entry.st_get_claimants(friends)

    with columns["Uneven split?"]:
        uneven_split = st.checkbox("Custom split?", key=f"unev_{entry.item_name}")

    if uneven_split:
        entry.st_get_uneven_split_weights()
    else:
        entry.reset_uneven_split_weights()

    st.markdown("---")


def split_bill(receipt: Receipt, friends: List[Friend]) -> None:

    if receipt is None:
        st.write(
            """
            No data here yet, please ensure that receipt has been properly scanned.
        """
        )
        return

    for entry in receipt.line_entries:
        if entry.is_valid:
            create_line_entry(entry, friends)
