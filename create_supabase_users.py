import os

from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = "https://ljcvameuyosoppzfmryo.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

emails = []#["t.schwarz@pkg-online.de"]
passwords = []#["srz_pkgonline"]

dict_users_lk_ph_abi28 = {
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

dicts = [dict_users_lk_ph_abi28]
for d in dicts:
    emails.extend(d.keys())
    passwords.extend(d.values())

for email, password in zip(emails, passwords):

    try:
        result = supabase.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True,  # User wird sofort als bestätigt markiert, kein Verify-Mail-Klick nötig
        })
        print(f"Angelegt: {email} -> {result.user.id}")
    except Exception as e:
        print(f"Fehler bei {email}: {e}")