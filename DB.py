import os
from supabase import create_client

class Singelton_db:
    _instance =None
    _voice_data = {}
    def __init__(self):
        raise RuntimeError
    
    @classmethod
    async def get_data_from_supabase(cls,userID:str):

        if cls._instance == None:
            cls._instance = cls.__new__(cls)

            url: str = os.environ.get("SUPABASE_URL")
            key: str = os.environ.get("SUPABASE_KEY")

            Client = create_client(url, key)
            voice_configuration = Client.table('voice_config').select('*').eq('chatbot_id',userID).execute()
            cls._voice_data = voice_configuration.data[0]

            return cls._voice_data
        
        return cls._voice_data
        