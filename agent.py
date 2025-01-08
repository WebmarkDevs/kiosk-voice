import json
import os
import logging
from DB import Singelton_db
from supabase import create_client
from dotenv import load_dotenv
import time
from livekit.agents import metrics
from fastapi import HTTPException
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    llm,
)
from pinecone import Pinecone
from openai import OpenAI
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import openai, deepgram, silero,google, elevenlabs
import requests
from apiHelper import *
from helper.func_calling import AssistantFnc
load_dotenv(dotenv_path=".env.local")
logger = logging.getLogger("voice-agent")


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()
# Define a path for the JSON file
USER_PHONE_MAPPING_FILE = "user_phone_mapping.json"

import json
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
sstart=0
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
client = OpenAI()  

async def getdata_api(query, namespace):
    top_k = 10 # Default number of results to return
    global sstart
    sstart = time.time()
    try:
        # Initialize Pinecone client
        index_name = os.getenv("PINECONE_INDEX_NAME")
        
        # Connect to index
        if index_name not in pc.list_indexes().names():
            return {"error": f"Index '{index_name}' does not exist", "statusCode": 404}
        start = time.time()   
        index = pc.Index(index_name)
        
        # Generate embedding for query
        # client = openai.OpenAI()
        # response = client.embeddings.create(
        #     input=query,
        #     model="text-embedding-ada-002"
        # )
        response = pc.inference.embed(
            model="multilingual-e5-large",
            inputs=[query],
            parameters={
                "input_type": "query"
            }
        )
        query_embedding = response.data[0].embedding
        # logger.info(query_embedding,"THIS IS THE QUERY EMBEDDING")
        end3 = time.time()
        logger.info("Embedding the input",end3-start)
        # Query Pinecone
        start = time.time()
        result = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            namespace=namespace,
            )
        end2 = time.time()
        print("&&&"*30)
        logger.info("result query time",end2-start)

        # logger.info(f"Query result: {result}")
        # Convert to dictionary if possible
        result_dict = result.to_dict()
        # logger.info(result_dict,"THIS IS THE RESULT DICT")

        matches = result_dict.get("matches", [])

        matched_arr = matches

        list_of_text=[]
        metadata=[]

        for match in matched_arr:
            list_of_text.append(match['metadata']['text'])
            if 'url' in match['metadata']:
                metadata.append(match['metadata']['url'])

        # print(list_of_text)
        # print(metadata)
        end = time.time()
        # logger.info("===="*40)
        logger.info("** TIME TAKEN **",end-start)
        return {"matches": list_of_text, "statusCode": 200,"metadata":metadata}
        
    except Exception as e:
        print('error-------------------',e)
        return {"error": str(e), "statusCode": 500}

# def getdata_api(query, userID):
#     global start
#     start = time.time()
#     logger.info("START")
#     url = os.environ.get("QUERY_API")
#     try:
#         payload = json.dumps({
#             "query_text": query,
#             "namespace": userID
#         })
#         headers = {
#             'Content-Type': 'application/json'
#         }
#         response = requests.post(url, headers=headers, data=payload)

#         # Log details
#         logger.info(f"Status Code: {response.status_code}")
#         logger.info(f"Request Headers: {headers}")
#         logger.info(f"Request Payload: {payload}")
#         logger.info(f"Response Headers: {response.headers}")
#         logger.info(f"Response Body: {response.text}")

#         if response.status_code == 403:
#             logger.error("403 Forbidden: Check your API key, headers, or permissions.")
        
#         response_data = response.json()
#         data = response_data.get("matches", "")
#         return data

#     except requests.exceptions.RequestException as e:
#         logger.error(f"Error occurred: {e}")
#         return ''

async def get_prompt(instructions,query,userID,voice_data):
        data = await getdata_api(query,userID)
        if data['statusCode'] == 500:
            print("Error is ------>>>>>",data['error'])
            return "sorry i have no content"
        
        #self.save_to_json(data)
        prompt = f"""
        Instructions you have to follow
        {instructions}
        ---------------------------
        Context information is below.
        ---------------------
        {data['matches']}
        ---------------------
        User question: [{query}]
        --------------------- 
        Please follow these guidelines when responding to queries: 
        {voice_data['prompt']}
        Answer:
        """
        
        return prompt  


# Utility function to load userID by phone number
def load_user_id_by_phone_number(phone_number: str) -> str:
    """Load userID by phone number from the JSON file."""
    try:
        with open(USER_PHONE_MAPPING_FILE, "r") as file:
            data = json.load(file)
        return data.get(phone_number, "UserID not found")
    except FileNotFoundError:
        return "Mapping file not found"


def switchProvider(voice_data):
    if voice_data['voice_provider'] == 'google':
        # logger.info("GOOGLE CREDENTIALS ------------------------->",json.load(os.environ.get('GOOGLE_CREDENTIALS')))
        credentials = {
            "type": os.environ.get("TYPE"),
            "project_id": os.environ.get("PROJECT_ID"),
            "private_key_id": os.environ.get("PRIVATE_KEY_ID"),
            "private_key": os.environ.get("PRIVATE_KEY"),
            "client_email": os.environ.get("CLIENT_EMAIL"),
            "client_id": os.environ.get("CLIENT_ID"),
            "auth_uri": os.environ.get("AUTH_URI"),
            "token_uri": os.environ.get("TOKEN_URI"),
            "auth_provider_x509_cert_url": os.environ.get("AUTH_PROVIDER_X509_CERT_URL"),
            "client_x509_cert_url": os.environ.get("CLIENT_X509_CERT_URL"),
            "universe_domain": os.environ.get("UNIVERSE_DOMAIN"),
        }
        print("THIS IS ------------",credentials)
        return google.TTS(voice_name=voice_data['voice_type'],credentials_info=credentials,speaking_rate=voice_data['speed'])
    
    elif voice_data['voice_provider'] == 'openai':
        return openai.TTS(voice=voice_data['voice_type'],speed=voice_data['speed'])
    



    
async def entrypoint(ctx: JobContext):
    logger.info(f"connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    participant = await ctx.wait_for_participant()
    logger.info(f"starting voice assistant for participant {participant.identity}")





    if "sip.trunkPhoneNumber" in participant.attributes:

        logger.info(f"Caller phone number is {participant.attributes['sip.trunkPhoneNumber']}")
        agent_metadata =  await get_metadata_by_number(participant.attributes['sip.trunkPhoneNumber'])
        userID = load_user_id_by_phone_number(participant.attributes['sip.trunkPhoneNumber'])
        message = (
            f"{agent_metadata.agent_prompts}"
            f"Use this information for calling functions that use UserID. UserID = {agent_metadata.userID}"
            "Do not provide userID to the user under any circumstances."
            "When a user wants to perform a function calling, help them generate relevant information, don't ask too many questions."
        )



    else:

        userID = participant.attributes['chatbot_id']
        logger.info('---------------------inside livekit voice------------------------------')
        logger.info(f"this is chabotId------>   {participant.attributes['chatbot_id']}")
        logger.info("--"*40)
        message= (
            f'You are a helpful AI voice assistant focused on customer service.'
            f"Use this information for calling functions that use UserID. UserID = {userID}"
            "Do not provide userID to the user under any circumstances."
            "When a user wants to perform a function calling, help them generate relevant information, don't ask too many questions."
        )
    


    
    # supabase se data
    
    initial_ctx = llm.ChatContext().append(
        role="system",
        text=message,
    )

    # userID = load_user_id_by_phone_number(participant.attributes['sip.trunkPhoneNumber'])

    # this is supabase voice_data
    voice_data = await Singelton_db.get_data_from_supabase(userID)
    


    async def truncate_context(assistant: VoicePipelineAgent,chat_ctx: llm.ChatContext):
        
        logger.info("this the zeroth index ------>",chat_ctx.messages[0].content)
        print("333"*30)
        logger.info("this is index number -1 ------>",chat_ctx.messages[-1].content)
        chat_ctx.messages[0].content = await get_prompt(chat_ctx.messages[0].content,chat_ctx.messages[-1].content,userID,voice_data)
        

        end = time.time()
        logger.info("TOTAL TIME TAKEN",end-sstart)


        if len(chat_ctx.messages) > 15:
            chat_ctx.messages = chat_ctx.messages[-15:]

       

    fnc_ctx = AssistantFnc()
    # Wait for the first participant to connect
    participant = await ctx.wait_for_participant()
    # logger.info(f"starting voice assistant for participant {participant.identity}")
    # logger.info(f"Caller phone number is {participant.attributes['sip.trunkPhoneNumber']}")
    # user data {voice_provider:'google'|'openai'}

    assistant = VoicePipelineAgent(
        vad=ctx.proc.userdata["vad"],
        stt=deepgram.STT(),
        llm=openai.LLM(model="gpt-4o-mini"),
        # tts=switchProvider(voice_data),
        tts = elevenlabs.TTS(),
        chat_ctx=initial_ctx,
        fnc_ctx=fnc_ctx,
        max_nested_fnc_calls=1,
        before_llm_cb=truncate_context,
        preemptive_synthesis=True, 
        min_endpointing_delay=0
    )
    assistant.start(ctx.room, participant)
    @assistant.on("metrics_collected")
    def _on_metrics_collected(mtrcs: metrics.AgentMetrics):
        # Use this helper to format and log based on metrics type
        metrics.log_metrics(mtrcs)
        print("++"*30)
        print("//"*30)
    
    # await assistant.say(voice_data['welcome_message'], allow_interruptions=True)
    await assistant.say(voice_data['welcome_message'], allow_interruptions=True)



if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        ),
    )
