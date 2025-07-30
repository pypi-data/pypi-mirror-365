from datetime import datetime
from faker import Faker


def get_new_email_with_timestamp():
    """
    Generates a new email address with a timestamp using Faker.
    """
    fake = Faker()
    # Generate a unique base for the email using Faker's safe_email or other methods
    # For a more "realistic" part before the +, you could use fake.user_name() or a part of fake.email()
    base_email_part = fake.user_name()  # e.g., 'john.doe' or 'mary_smith'

    time_stamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    return f"{base_email_part}+{time_stamp}@groupebeaumanoir.fr"
