import configparser
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import os

from dotenv import load_dotenv
from supabase import create_client, Client

x = 1
if x:
    CREATE_USERS    = True#False#
    DELETE_USERS    = False#True#
    SEND_MAIL       = True#False#

else:
    CREATE_USERS    = False#True#
    DELETE_USERS    = True#False#
    SEND_MAIL       = False#

# User credentials live outside this file (not tracked by git) so no
# passwords end up in the repository. Format: an .ini file with one
# section per group, each line "email = password". See users.example.ini
# for a template.
USERS_FILE = "users.ini"

if not os.path.exists(USERS_FILE):
    raise SystemExit(
        f"User data file not found: {USERS_FILE}\n"
        f"Create it next to this script (see users.example.ini for the format)."
    )

user_config = configparser.ConfigParser()
user_config.optionxform = str  # keep email addresses in their original case
user_config.read(USERS_FILE, encoding="utf-8")
user_groups = {section: dict(user_config.items(section)) for section in user_config.sections()}

test_dict = user_groups.get("test", {})
users_lk_ph_abi28_dict = user_groups.get("lk_ph_abi28", {})

user_dicts = [users_lk_ph_abi28_dict]##[test_dict]##

load_dotenv()

SMTP_HOST = "mail.nrw.schule"
SMTP_PORT = 465
SMTP_USER = "t.schwarz@pkg-overath.de"
SMTP_PASSWORD = os.environ["SMTP_PASSWORD"]  # dein normales LOGINEO-NRW-Passwort

def send_credentials_email(to_email: str, password: str):
    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = "Deine Zugangsdaten"

    body = f"""
    Hallo,

    dein Zugang für die datenbankgestütze Nutzung der interaktiven Lernmaterialien des PKG wurde angelegt.

    Benutzername: {to_email}
    Passwort: {password}

    Teste deinen Account auf: https://thomasschwarz-github.github.io/pkg_digitale_materialien_physik_informatik/.
    Bei Fragen oder Problemen wende dich bitte an: t.schwarz@pkg-overath.de oder t.schwarz@pkg-online.de
    """
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:  # SMTP_SSL statt SMTP
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)

    # with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
    #     server.starttls()
    #     server.login(SMTP_USER, SMTP_PASSWORD)
    #     server.send_message(msg)


SUPABASE_URL = "https://ljcvameuyosoppzfmryo.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

if CREATE_USERS and DELETE_USERS:
    raise SystemExit("CREATE_USERS and DELETE_USERS must not both be True at the same time.")

emails = []
passwords = []

for user_dict in user_dicts:
    emails.extend(user_dict.keys())
    passwords.extend(user_dict.values())

if DELETE_USERS:
    response = supabase.auth.admin.list_users(page=1, per_page=1000)
    all_users = getattr(response, "users", response)  # list or object with .users, depending on supabase-py version
    email_to_id = {user.email: user.id for user in all_users}

for email, password in zip(emails, passwords):
    if CREATE_USERS:
        try:
            result = supabase.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True,  # user is immediately marked as confirmed, no verification email click needed
            })
            print(f"Created: {email} -> {result.user.id}")
        except Exception as e:
            print(f"Error for {email}: {e}")
    if SEND_MAIL:
        try:
            send_credentials_email(email, password)
            print(f"Email sent: {email}")
        except Exception as e:
            print(f"Error sending email to {email}: {e}")

    if DELETE_USERS:
        user_id = email_to_id.get(email)
        if user_id is None:
            print(f"Not found (skipped): {email}")
            continue
        try:
            supabase.auth.admin.delete_user(user_id)
            print(f"Deleted: {email} -> {user_id}")
        except Exception as e:
            print(f"Error deleting {email}: {e}")
