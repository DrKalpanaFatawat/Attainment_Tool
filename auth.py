import streamlit as st
import re

from database import (
    create_user,
    authenticate_user,
    update_last_login,
    record_activity,
)


def render_auth_page():
    st.title("Attainment Registration and Login")
    
    login_tab, register_tab = st.tabs(
        ["Login", "Faculty Registration"]
    )

    with login_tab:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input(
                "Password", type="password"
            )
            submitted = st.form_submit_button(
                "Login", type="primary"
            )

        if submitted:
            username = username.strip().lower()

            # Avoid unnecessarily expensive password checks
            # for oversized input.
            if len(username) > 50 or len(password) > 128:
                user = None
            else:
                user = authenticate_user(username, password)

            if user is None:
                record_activity(
                    None, username or "unknown",
                    "LOGIN", status="FAILED"
                )
                st.error("Invalid credentials or inactive account.")
            else:
                update_last_login(user["id"])
                record_activity(
                    user["id"], user["username"],
                    "LOGIN", status="SUCCESS"
                )

                st.session_state["authenticated"] = True
                st.session_state["user_id"] = user["id"]
                st.session_state["username"] = user["username"]
                st.session_state["full_name"] = user["full_name"]
                st.session_state["department"] = user["department"]
                st.session_state["role"] = user["role"]

                st.rerun()

    with register_tab:
        st.info(
            "Register a faculty account. "      )

        with st.form("registration_form"):
            full_name = st.text_input("Full name")
            department = st.text_input("Department")
            new_username = st.text_input("Choose username")
            new_password = st.text_input(
                "Choose password", type="password"
            )
            confirm_password = st.text_input(
                "Confirm password", type="password"
            )

            registered = st.form_submit_button(
                "Create Faculty Account"
            )

        if registered:
            valid_username = bool(
                re.fullmatch(r"[A-Za-z0-9_.-]{4,50}", new_username)
            )

            if not full_name.strip():
                st.error("Enter your full name.")
            elif not valid_username:
                st.error(
                    "Username must be 4–50 characters: "
                    "letters, numbers, dot, underscore or hyphen."
                )
            elif len(new_password) < 8:
                st.error(
                    "Use a password with at least 8 characters."
                )
            elif len(new_password) > 14:
                st.error("Password is too long.")
            elif new_password != confirm_password:
                st.error("The passwords do not match.")
            else:
                ok, message = create_user(
                    username=new_username,
                    password=new_password,
                    full_name=full_name,
                    department=department,
                    role="faculty"
                )

                if ok:
                    record_activity(
                        None, new_username.strip().lower(),
                        "REGISTER", status="SUCCESS"
                    )
                    st.success(message)
                else:
                    st.error(message)


def require_login():
    if not st.session_state.get("authenticated", False):
        render_auth_page()
        st.stop()


def logout():
    if st.sidebar.button("Logout", key="logout_button"):
        user_id = st.session_state.get("user_id")
        username = st.session_state.get("username", "")

        if user_id:
            record_activity(
                user_id,
                username,
                "LOGOUT",
                status="SUCCESS"
            )

        # Clear the session only after the button is clicked.
        for key in list(st.session_state.keys()):
            del st.session_state[key]

        st.rerun()
