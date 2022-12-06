import streamlit as st
from typing import List, Union
from dataclasses import dataclass

from src.models import Receipt, LineEntry, Friend, Claim


@dataclass
class ColumnSpec:
    name: str
    width: int


SPLIT_COLUMNS = [
    ColumnSpec(name="Item", width=3),
    ColumnSpec(name="Claimants", width=2),
    ColumnSpec(name="Uneven split?", width=1)
]


def get_column_widths() -> List[int]:
    return [c.width for c in SPLIT_COLUMNS]


def get_column_names() -> List[str]:
    return [c.name for c in SPLIT_COLUMNS]


def filter_friend_from_name(friends: List[Friend], name: str) -> Union[Friend, None]:
    matching_friends = list(filter(lambda f: f.name == name, friends))
    if len(matching_friends) == 1:
        return matching_friends[0]
    elif len(matching_friends) == 0:
        return None
    else:
        raise ValueError(f"{len(matching_friends)} friends found with {name=}")


def create_line_entry(entry: LineEntry, friends: List[Friend]):

    columns = dict(zip(get_column_names(), st.columns(get_column_widths())))

    with columns["Item"]:
        st.markdown(f"{entry.item_name} | **£{entry.item_cost:.2f}**")

    with columns["Claimants"]:
        claimants_names = st.multiselect(
            "Claimants", 
            [f.name for f in friends], 
            # label_visibility="collapsed", 
            key=f"claimants_{entry.item_name}"
        )
        claimants = [
            filter_friend_from_name(friends, claimant_name)
            for claimant_name in claimants_names
        ]
        entry.claims = [Claim(claimant=c) for c in claimants]

    with columns["Uneven split?"]:
        uneven_split = st.checkbox("Custom split?", key=f"unev_{entry.item_name}")

    if uneven_split:
        for claim in entry.claims:
            claim.portion = st.number_input(
                claim.claimant.name,
                value=1,
                key=f"prop_{claim.claimant.name}_{entry.item_name}"
            )
    else:
        for claim in entry.claims:
            # Make sure to reset proportion to 1 for all claims
            # if uneven_split becomes unchecked again
            claim.portion = 1

    st.markdown("---")


def split_bill(receipt: Receipt, friends: List[Friend]) -> None:
    for entry in receipt.line_entries:
        if entry.is_valid:
            create_line_entry(entry, friends)
