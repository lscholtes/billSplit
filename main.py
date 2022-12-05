import streamlit as st

from src.friends import parse_friends
from src.scan import crop_parse_clean
from src.split import split_bill
from src.summary import summarize


st.set_page_config(layout="wide")
scan_tab, friends_tab, split_tab, summary_tab = st.tabs(["Scan", "Friends", "Split", "Summary"])

receipt_image = st.sidebar.file_uploader("Upload image")

if receipt_image:

    with scan_tab:
        receipt = crop_parse_clean(receipt_image)

    with friends_tab:
        friends = parse_friends()

    with split_tab:
        split_bill(receipt, friends)

    with summary_tab:
        summarize(receipt, friends)