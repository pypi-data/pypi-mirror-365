
import os
import sys
import streamlit as st

# Get the absolute path to the parent directory (rockyroad_tools)
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Insert the path to the rockyroad_tools directory into sys.path
sys.path.insert(0, parent_dir)


def run():
    from streamlit_rockyroad_tools import st_notification_bar
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
