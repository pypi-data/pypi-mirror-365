
import os
import sys
import streamlit as st

# Get the absolute path to the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Insert the path to the streamlit_fastselectbox directory into sys.path
sys.path.insert(0, os.path.join(current_dir, '..'))


def run():
    from st_notification_bar import st_notification_bar
    st.set_page_config(page_title="Notification Bar Example", layout="wide")
    st.subheader("Component with constant args")

    st_notification_bar(
        message="This is a notification bar from our sponsors.",
        learn_more="https://streamlit.io",
        key="notification_bar_test_1",
    )

    st_notification_bar(
        message="And here's another notification bar from our sponsors.",
        learn_more="https://streamlit.io",
        key="notification_bar_test_3",
    )


if __name__ == "__main__":
    run()
