import streamlit as st

HELP_TEXT = """
# Welcome to BillSplit!

BillSplit helps you split long bills between your friends:

1) 📷 Upload a picture of the bill. It helps if the picture shows only the \
    line items on the receipt!
2) 🤖 The app uses an AI algorithm* to scan the picture and extract all \
    available text.
3) 🖹 In the *Scan* tab, the extracted text is shown. At this point it's up to \
    you to fix any obvious mistakes, like incorrect prices or formatting. The \
    app expects **one line item per line, with the total price of that line \
    item at the end** (whitespace is fine, it's handled automatically).
4) 👪 In the *Friends* tab, add the names of everyone who you're splitting \
    with as a comma-separated list.
5) 🔀 In the *Split* tab, go through each line entry and assign them to their \
     owner(s). Note that if there are multiple owners but you don't want to
     split the entry evenly, you can click the `Custom split` checkbox.
6) 💸 In the *Summary* tab you can see how much each person owes, and you \
    have the option to add a tip if you'd like.

## Tips
* When splitting an item with the `Custom split` option, the values given \
    are treated as a relative weighting, e.g. if A and B are splitting £10 \
    and A has weight 2 and B has 3, then A pays £4 and B pays £6.
* If the extracted text on the *Scan* tab isn't very good, try toggling the \
    `Alternate OCR PSM` checkbox. This runs the text recognition AI slightly \
    differently and sometimes yields improved results.

---

Source code for BillSplit can be found [here](https://github.com/lscholtes/billSplit).

---

*\* Tesseract 4 OCR engine*
"""


def display_help():
    st.markdown(HELP_TEXT)
