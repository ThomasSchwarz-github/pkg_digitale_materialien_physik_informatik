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

test_dict = {"j.haas@pkg-overath.de": "js_1234"}#{"t.schwarz@pkg-online.de": "srz_pkgonline"}

users_lk_ph_abi28_dict = {
    "johannes.friedrich@pkg-online.de" : "jf_2137",
    "tristan.hartmann@pkg-online.de" : "th_3948",
    "simon.haupts@pkg-online.de" : "sh_9416",
    "samuel.horvath@pkg-online.de" : "sh_1872",
    "alina.klug@pkg-online.de" : "ak_2787",
    "julian.lenz@pkg-online.de" : "jl_1954",
    "jeremias.nitzschmann@pkg-online.de" : "jn_4496",
    "kateryna.rudaieva@pkg-online.de" : "kr_7218",
    "ben.sass@pkg-online.de" : "bs_7729",
    "moritz.schlegel@pkg-online.de" : "ms_8821"
    }

user_dicts = [test_dict]##[users_lk_ph_abi28_dict]

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
