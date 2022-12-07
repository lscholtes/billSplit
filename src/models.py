import re
from dataclasses import dataclass
from typing import List, Union

import streamlit as st


@dataclass
class Friend:

    name: str


@dataclass
class Claim:

    claimant: Friend
    weight: float = 1


@dataclass
class LineEntry:

    item_name: str = None
    item_cost: float = None
    claims: List[Claim] = None
    is_valid: bool = True

    @classmethod
    def parse_line_entry_str(cls, line_entry_str: str):

        # Assume that the last number with two decimal places in the line is
        # the total price for that entry. Note that we reverse the string to
        # search from the end
        line_entry_str_rev = line_entry_str[::-1]
        price_regex = r"\d{2}(?: *(?:\.|,) *)+\d*"
        price_matches = re.findall(price_regex, line_entry_str_rev)

        if not price_matches:
            return cls(is_valid=False)
        else:
            # Grab the first match found in the reversed string and reverse it
            # again to get the original number
            price_str = price_matches[0][::-1]

        try:
            # Convert commas to decimal points, remove any whitespace
            price = float(price_str.replace(",", ".").replace(" ", ""))
        except ValueError:
            # If we can't convert to float, mark as invalid
            return cls(is_valid=False)

        # Once we've grabbed the price, assume that everything that comes
        # before the last occurence of the price is the item name.
        name_regex = rf"(.*){price_str}"
        name_match = re.search(name_regex, line_entry_str)
        if name_match is None:
            return cls(is_valid=False)
        (name,) = name_match.groups()

        return cls(item_name=name, item_cost=price)

    @property
    def sum_claimed_weights(self):
        return sum(claim.weight for claim in self.claims)

    def get_claim_by_friend(self, friend: Friend) -> Union[Claim, None]:

        matching_claims = list(filter(lambda c: c.claimant == friend, self.claims))

        if len(matching_claims) == 1:
            return matching_claims[0]
        elif len(matching_claims) == 0:
            return None
        else:
            raise ValueError(f"{len(matching_claims)} claims found with {friend=}")

    def st_get_claimants(self, friends: List[Friend]) -> None:

        claimants_names = st.multiselect(
            "Claimants",
            [f.name for f in friends],
            # label_visibility="collapsed",
            key=f"claimants_{self.item_name}",
        )

        claimants = [
            self._get_friend_from_name(friends, claimant_name)
            for claimant_name in claimants_names
        ]

        self.claims = [Claim(claimant=c) for c in claimants]

    def st_get_uneven_split_weights(self) -> None:
        for claim in self.claims:
            claim.weight = st.number_input(
                claim.claimant.name,
                value=1,
                key=f"prop_{claim.claimant.name}_{self.item_name}",
            )

    def reset_uneven_split_weights(self) -> None:
        if self.claims:
            for claim in self.claims:
                claim.weight = 1

    @staticmethod
    def _get_friend_from_name(friends: List[Friend], name: str) -> Union[Friend, None]:

        matching_friends = list(filter(lambda f: f.name == name, friends))

        if len(matching_friends) == 1:
            return matching_friends[0]
        elif len(matching_friends) == 0:
            return None
        else:
            raise ValueError(f"{len(matching_friends)} friends found with {name=}")


@dataclass
class Receipt:

    line_entries: List[LineEntry]

    @classmethod
    def parse_receipt_text(cls, receipt_str: str):
        line_entries = [
            LineEntry.parse_line_entry_str(line) for line in receipt_str.split("\n")
        ]
        return Receipt(line_entries=line_entries)

    @property
    def total_cost(self):
        return sum(item.item_cost for item in self.line_entries if item.is_valid)

    def get_items_claimed_by_friend(self, friend: Friend) -> List[LineEntry]:
        return list(
            filter(
                lambda item: (item.claims is not None)
                and any(claim.claimant == friend for claim in item.claims),
                self.line_entries,
            )
        )

    def get_total_cost_claimed_by_friend(self, friend: Friend) -> float:
        items_claimed = self.get_items_claimed_by_friend(friend)
        total_cost = sum(
            item.item_cost
            * item.get_claim_by_friend(friend).weight
            / item.sum_claimed_weights
            for item in items_claimed
        )
        return total_cost

    def st_add_tip(self, friends: List[Friend]) -> None:
        tip_checbox_col, tip_amount_col, _ = st.columns([1, 1, 3])

        with tip_checbox_col:
            add_tip = st.radio("Add tip/tax?", ["No tip", "Even split", "Custom split"])

        if add_tip != "No tip":
            with tip_amount_col:
                tip_amount = float(st.text_input("Tip amount", 0))

        if add_tip == "Even split":
            self._even_tip_split(tip_amount, friends)

        if add_tip == "Custom split":
            self._st_custom_tip_split(tip_amount, friends)

    def _even_tip_split(self, tip_amount: float, friends: List[Friend]) -> None:
        self.line_entries.append(
            LineEntry(
                item_name="Tip",
                item_cost=tip_amount,
                claims=[Claim(claimant=f) for f in friends],
            )
        )

    def _st_custom_tip_split(self, tip_amount: float, friends: List[Friend]) -> None:

        st.markdown(
            "_Quick Tip: The fields below are pre-filled with the amount all \
            participants claimed -  this means each diner pays a tip \
            precisely on what they bought._"
        )

        tip_line_entry = LineEntry(item_name="Tip", item_cost=tip_amount, claims=[])

        tip_weight_cols = st.columns(len(friends))
        for i, friend in enumerate(friends):
            with tip_weight_cols[i]:
                st.markdown(friend.name)

        for i, friend in enumerate(friends):
            with tip_weight_cols[i]:
                tip_weight = st.text_input(
                    f"tip_prop_{friend.name}",
                    value=self.get_total_cost_claimed_by_friend(friend),
                    label_visibility="collapsed",
                )
                tip_line_entry.claims.append(
                    Claim(claimant=friend, weight=float(tip_weight))
                )

        self.line_entries.append(tip_line_entry)

    def st_check_total_against_claimed(self, friends: List[Friend]) -> None:

        total_claimed = sum(
            self.get_total_cost_claimed_by_friend(friend) for friend in friends
        )

        if total_claimed != self.total_cost:
            st.markdown(
                f"""
                ## Wait! ⚠️
                **The amount claimed, £{total_claimed:.2f}, does not \
                match the total bill amount.**  
                *Make sure all items have been claimed on the Split tab.*"""
            )
        st.markdown(f"## Total cost: £{self.total_cost:.2f}")
