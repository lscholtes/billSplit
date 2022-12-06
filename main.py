import streamlit as st

from src.friends import parse_friends
from src.scan import parse_and_clean
from src.split import split_bill
from src.summary import summarize
from src.upload import upload_and_crop


upload_tab, scan_tab, friends_tab, split_tab, summary_tab = st.tabs(["Upload", "Scan", "Friends", "Split", "Summary"])

with upload_tab:
    receipt_image = upload_and_crop()

if receipt_image:

    with scan_tab:
        receipt = parse_and_clean(receipt_image)

    with friends_tab:
        friends = parse_friends()

    with split_tab:
        split_bill(receipt, friends)

    with summary_tab:
        summarize(receipt, friends)
