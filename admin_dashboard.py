import streamlit as st
import pandas as pd

from database import (
    get_dashboard_summary,
    get_activity_logs,
    get_users,
    set_user_status,
    record_activity,
    reset_faculty_password,
)
from auth import logout


def render_admin_dashboard():
    # Always check the authenticated role before displaying
    # administrator information.
    if not st.session_state.get("authenticated"):
        st.error("Please log in.")
        st.stop()

    if st.session_state.get("role") != "admin":
        st.error("You are not authorized to access this dashboard.")
        st.stop()

    st.title("Administrator Dashboard")
    st.caption("Attainment Automation — Activity Monitoring")

    summary = get_dashboard_summary()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Registered Faculty", summary["faculty"])
    c2.metric("Active Faculty", summary["active_faculty"])
    c3.metric("Sheets Generated", summary["generated"])
    c4.metric("Failed Logins", summary["failed_logins"])

    st.divider()

    logs_tab, faculty_tab = st.tabs(
        ["Activity Logs", "Faculty Accounts"]
    )

    with logs_tab:
        st.subheader("Recent Activity")

        limit = st.selectbox(
            "Records to display",
            [100, 250, 500, 1000, 2000],
            index=2
        )

        logs = get_activity_logs(limit)

        if logs:
            df = pd.DataFrame(logs)

            action_filter = st.multiselect(
                "Filter activity",
                sorted(df["action"].dropna().unique().tolist())
            )

            status_filter = st.multiselect(
                "Filter status",
                sorted(df["status"].dropna().unique().tolist())
            )

            if action_filter:
                df = df[df["action"].isin(action_filter)]

            if status_filter:
                df = df[df["status"].isin(status_filter)]

            st.dataframe(df, use_container_width=True)

            st.download_button(
                "Download Activity Log CSV",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="attainment_activity_logs.csv",
                mime="text/csv"
            )
        else:
            st.info("No activity has been recorded yet.")

    with faculty_tab:
        st.subheader("Registered Faculty")

        users = get_users()
        faculty = [
            user for user in users
            if user["role"] == "faculty"
        ]

        if faculty:
            st.dataframe(
                pd.DataFrame(faculty),
                use_container_width=True
            )

            st.subheader("Change Faculty Account Status")

            account_options = {
                f'{u["username"]} — {u["full_name"]} '
                f'({u["status"]})': u
                for u in faculty
            }

            selected_label = st.selectbox(
                "Select faculty account",
                list(account_options.keys())
            )

            selected_user = account_options[selected_label]

            new_status = st.radio(
                "New status",
                ["active", "disabled"],
                horizontal=True,
                index=0 if selected_user["status"] == "active" else 1
            )

            if st.button("Update Account Status"):
                if new_status != selected_user["status"]:
                    set_user_status(
                        selected_user["id"], new_status
                    )

                    record_activity(
                        st.session_state["user_id"],
                        st.session_state["username"],
                        "ACCOUNT_STATUS_CHANGE",
                        status="SUCCESS",
                        details=(
                            f'Account {selected_user["username"]}: '
                            f'{new_status}'
                        )
                    )

                    st.success("Account status updated.")
                    st.rerun()
                else:
                    st.info("The account already has this status.")
        else:
            st.info("No faculty accounts are registered.")

    st.divider()
    st.divider()
    st.subheader("Reset Faculty Password")

    if faculty:
            reset_username = st.selectbox(
                "Select faculty member",
                [u["username"] for u in faculty],
                key="reset_faculty_username"
            )

            with st.form("reset_password_form"):
                new_password = st.text_input(
                    "New temporary password",
                    type="password"
                )
                confirm_password = st.text_input(
                    "Confirm temporary password",
                    type="password"
                )
                submitted = st.form_submit_button(
                    "Reset Password",
                    type="primary"
                )

            if submitted:
                if len(new_password) < 8:
                    st.error("Password must be at least 8 characters.")
                elif len(new_password) > 14:
                    st.error("Password must not exceed 14 characters.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    try:
                        success = reset_faculty_password(
                            reset_username,
                            new_password
                        )

                        if success:
                            record_activity(
                                st.session_state["user_id"],
                                st.session_state["username"],
                                "PASSWORD_RESET",
                                status="SUCCESS",
                                details=f"Password reset for {reset_username}"
                            )
                            st.success("Faculty password reset successfully.")
                        else:
                            st.error("Password reset failed.")

                    except ValueError as e:
                        st.error(str(e))
                    else:
                        st.info("No faculty accounts are available.")

            logout()