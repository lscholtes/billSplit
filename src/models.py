from dataclasses import dataclass
import re
from typing import List, Union


@dataclass
class Friend:

    # Perhaps slight overkill to have a dataclass with a single attribute but
    # it makes it easier to reason about the objects being passed around, and
    # in future I may want to add email addresses or bank details to each person

    name: str


@dataclass
class Claim:
    claimant: Friend
    portion: Union[float, int] = 1


@dataclass
class LineEntry:

    item_name: str = None
    item_cost: float = None
    claims: List[Claim] = None
    is_valid: bool = True

    @classmethod
    def parse_line_entry_str(cls, line_entry_str: str):

        # Assume that the last number with two decimal places in the line is the total price for that entry.
        # Note that we reverse the string to search from the end
        line_entry_str_rev = line_entry_str[::-1]
        price_regex = r"\d{2}(?: *(?:\.|,) *)+\d*"
        price_matches = re.findall(price_regex, line_entry_str_rev)

        if not price_matches:
            return cls(is_valid=False)
        else:
            # Grab the first match found in the reversed string and reverse it again to get the original number
            price_str = price_matches[0][::-1]

        try:
            # Convert commas to decimal points, remove any whitespace
            price = float(price_str.replace(",", ".").replace(" ", ""))
        except ValueError:
            # If for some reason we still can't convert to float, just mark as invalid
            return cls(is_valid=False)

        # Once we've grabbed the price, assume that everything that comes before the last occurence of the
        # price is the item name.
        name_regex = rf"(.*){price_str}"
        name_match = re.search(name_regex, line_entry_str)
        if name_match is None:
            return cls(is_valid=False)
        (name,) = name_match.groups()

        return cls(item_name=name, item_cost=price)

    @property
    def total_claimed_portions(self):
        return sum(claim.portion for claim in self.claims)


@dataclass
class Receipt:

    line_entries: List[LineEntry]

    @classmethod
    def parse_receipt_text(cls, receipt_str: str):
        line_entries = [
            LineEntry.parse_line_entry_str(line) for line in receipt_str.split("\n")
        ]
        return Receipt(line_entries=line_entries)
