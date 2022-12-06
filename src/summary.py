from typing import List, Union

import streamlit as st

from src.models import Claim, Friend, LineEntry, Receipt


def filter_claims_for_claimant(
    claims: List[Claim], friend: Friend
) -> Union[Claim, None]:
    matching_claims = list(filter(lambda c: c.claimant == friend, claims))
    if len(matching_claims) == 1:
        return matching_claims[0]
    elif len(matching_claims) == 0:
        return None
    else:
        raise ValueError(f"{len(matching_claims)} claims found with {friend=}")


def get_items_claimed_for_friend(receipt: Receipt, friend: Friend) -> List[LineEntry]:
    return list(
        filter(
            lambda item: (item.claims is not None)
            and any(claim.claimant == friend for claim in item.claims),
            receipt.line_entries,
        )
    )


def get_total_cost_for_friend(items: List[LineEntry], friend: Friend) -> float:
    total_cost = sum(
        item.item_cost
        * filter_claims_for_claimant(item.claims, friend).portion
        / item.total_claimed_portions
        for item in items
    )
    return total_cost


def summarize(receipt: Receipt, friends: List[Friend]):

    total_cost_without_tip = sum(
        item.item_cost for item in receipt.line_entries if item.is_valid
    )
    st.markdown(f"**Total cost, without tip:** £{total_cost_without_tip:.2f}")

    tip_checbox_col, tip_amount_col, _ = st.columns([1, 1, 3])

    with tip_checbox_col:
        add_tip = st.radio("Add tip?", ["No tip", "Even split", "Custom split"])

    if add_tip != "No tip":
        with tip_amount_col:
            total_tip = float(st.text_input("Total tip", 0))

    if add_tip == "Even split":
        receipt.line_entries.append(
            LineEntry(
                item_name="Tip",
                item_cost=total_tip,
                claims=[Claim(claimant=f) for f in friends],
            )
        )

    if add_tip == "Custom split":
        st.markdown(
            "_Quick Tip: The fields below are pre-filled with the amount all \
            participants paid -  this means each diner pays a tip \
            precisely on what they bought._"
        )

        tip_line_entry = LineEntry(item_name="Tip", item_cost=total_tip, claims=[])

        tip_portion_cols = st.columns(len(friends))
        for i, friend in enumerate(friends):
            with tip_portion_cols[i]:
                st.markdown(friend.name)

        for i, friend in enumerate(friends):
            items_claimed = get_items_claimed_for_friend(receipt, friend)
            total_cost = get_total_cost_for_friend(items_claimed, friend)
            with tip_portion_cols[i]:
                tip_portion = st.text_input(
                    label=f"tip_prop_{friend.name}",
                    value=total_cost,
                    label_visibility="collapsed",
                )
                tip_line_entry.claims.append(
                    Claim(claimant=friend, portion=float(tip_portion))
                )

        receipt.line_entries.append(tip_line_entry)

    total_cost = sum(item.item_cost for item in receipt.line_entries if item.is_valid)
    total_claimed = sum(
        get_total_cost_for_friend(get_items_claimed_for_friend(receipt, friend), friend)
        for friend in friends
    )

    st.markdown(f"## Total cost: £{total_cost:.2f}")

    if total_claimed != total_cost:
        st.markdown(
            f"""**Careful! The amount claimed, £{total_claimed:.2f}, does not \
                match the total bill amount.** 
                *Make sure all items have been claimed on the Split tab.*"""
        )

    for friend in friends:
        items_claimed = get_items_claimed_for_friend(receipt, friend)
        total_cost = get_total_cost_for_friend(items_claimed, friend)

        st.markdown(
            f"{friend.name} | **£{total_cost:.2f}** | \
                {', '.join([item.item_name for item in items_claimed])}"
        )
