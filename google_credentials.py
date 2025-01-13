import os
from DB import Singelton_db

async def google_credentials_info(userID):

    voice_data = await Singelton_db.get_data_from_supabase(userID)
    credentials = {
                "type": os.environ.get("TYPE"),
                "project_id": os.environ.get("PROJECT_ID"),
                "private_key_id": os.environ.get("PRIVATE_KEY_ID"),
                # "private_key": os.environ.get("PRIVATE_KEY"),
                "private_key": voice_data["google_private_key"],
                "client_email": os.environ.get("CLIENT_EMAIL"),
                "client_id": os.environ.get("CLIENT_ID"),
                "auth_uri": os.environ.get("AUTH_URI"),
                "token_uri": os.environ.get("TOKEN_URI"),
                "auth_provider_x509_cert_url": os.environ.get("AUTH_PROVIDER_X509_CERT_URL"),
                "client_x509_cert_url": os.environ.get("CLIENT_X509_CERT_URL"),
                "universe_domain": os.environ.get("UNIVERSE_DOMAIN"),
            }
    return credentials