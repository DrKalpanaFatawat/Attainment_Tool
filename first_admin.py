from getpass import getpass

from database import initialize_database, create_first_admin


def main():
    initialize_database()

    print("Create the first Attainment Tool administrator.")

    username = input("Admin username: ").strip()
    full_name = input("Admin full name: ").strip()
    password = getpass("Admin password (12+ characters): ")
    confirm = getpass("Confirm admin password: ")

    if password != confirm:
        print("Passwords do not match.")
        return

    try:
        create_first_admin(username, password, full_name)
        print("Administrator account created.")
    except (ValueError, Exception) as exc:
        print(f"Could not create administrator: {exc}")


if __name__ == "__main__":
    main()