from typing import List

import streamlit as st

from src.models import Friend, Receipt


def summarize(receipt: Receipt, friends: List[Friend]) -> None:

    st.markdown(f"**Total cost, without tip:** £{receipt.total_cost:.2f}")

    receipt.st_add_tip(friends)
    receipt.st_check_total_against_claimed(friends)

    for friend in friends:

        items_claimed_str = ", ".join(
            [item.item_name for item in receipt.get_items_claimed_by_friend(friend)]
        )

        st.markdown(
            f"{friend.name} | \
            **£{receipt.get_total_cost_claimed_by_friend(friend):.2f}** | \
            {items_claimed_str}"
        )
