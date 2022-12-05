import streamlit as st
from typing import List, Union
from dataclasses import dataclass

from src.models import Receipt, LineEntry, Friend, Claim


@dataclass
class ColumnSpec:
    name: str
    width: int


SPLIT_COLUMNS = [
    ColumnSpec(name="Name", width=3),
    ColumnSpec(name="Total Cost", width=1),
    ColumnSpec(name="Claimants", width=3),
    ColumnSpec(name="Uneven split?", width=1),
    ColumnSpec(name="Claimant", width=1),
    ColumnSpec(name="Portion", width=1)
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

        with columns["Name"]:
            st.write(entry.item_name)
        
        with columns["Total Cost"]:
            st.markdown(f"£{entry.item_cost:.2f}")

        with columns["Claimants"]:
            claimants_names = st.multiselect(
                "claimants", 
                [f.name for f in friends], 
                label_visibility="collapsed", 
                key=f"claimants_{entry.item_name}"
            )
            claimants = [
                filter_friend_from_name(friends, claimant_name)
                for claimant_name in claimants_names
            ]
            entry.claims = [Claim(claimant=c) for c in claimants]

        with columns["Uneven split?"]:
            uneven_split = st.checkbox("", key=f"unev_{entry.item_name}")

        if uneven_split:
            for claim in entry.claims:
                with columns["Claimant"]:        
                    st.markdown(claim.claimant.name)
                with columns["Portion"]:
                    claim.portion = float(st.text_input(
                        f"prop_{claim.claimant.name}_{entry.item_name}", 
                        value="1", 
                        label_visibility="collapsed"
                    ))
        else:
            for claim in entry.claims:
                # Make sure to reset proportion to 1 for all claims
                # if uneven_split becomes unchecked again
                claim.portion = 1


def split_bill(receipt: Receipt, friends: List[Friend]) -> None:
    # Write table header
    split_table_columns = dict(zip(get_column_names(), st.columns(get_column_widths())))
    for col_name, col in split_table_columns.items():
        with col:           
            st.write(f"**{col_name}**")

    # Write table entries
    if receipt:
        for entry in receipt.line_entries:
            if entry.is_valid:
                create_line_entry(entry, friends)
