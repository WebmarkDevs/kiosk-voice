import json
import os
import logging
from DB import Singelton_db
from google_credentials import google_credentials_info
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

        response = client.embeddings.create(
            input=query,
            model="text-embedding-ada-002"
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
        logger.info("result query time",end2-start)


        result_dict = result.to_dict()

        matches = result_dict.get("matches", [])

        matched_arr = matches

        list_of_text=[]
        metadata=[]

        for match in matched_arr:
            list_of_text.append(match['metadata']['text'])
            if 'url' in match['metadata']:
                metadata.append(match['metadata']['url'])

        end = time.time()
        logger.info("** TIME TAKEN **",end-start)
        return {"matches": list_of_text, "statusCode": 200,"metadata":metadata}
        
    except Exception as e:
        print('error-------------------',e)
        return {"error": str(e), "statusCode": 500}


async def get_prompt(instructions,query,userID,voice_data):
        data = await getdata_api(query,userID)
        print(data["statusCode"])
        if data['statusCode'] == 500 :
            print("Error is ------>>>>>",data['error'])
            return "error"
        
        elif data["statusCode"] == 404:
            return 'error'

        #self.save_to_json(data)
        prompt = f"""
        Instructions you have to follow
        {instructions}
        Context information is below.
        ---------------------
        {data['matches']}
        ---------------------
        User question: [{query}]
        ---------------------
        
        Please follow these guidelines when responding to queries: 
        {voice_data['prompt']}
        
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



async def switchProvider(voice_data):
    if voice_data['voice_provider'] == 'google':

        # logger.info("GOOGLE CREDENTIALS ------------------------->",json.load(os.environ.get('GOOGLE_CREDENTIALS')))
        credentials = await google_credentials_info(voice_data['chatbot_id'])
        print("THIS IS ------------",credentials)
        return google.TTS(voice_name=voice_data['voice_type'],credentials_info=credentials,speaking_rate=voice_data['speed'])
    
    elif voice_data['voice_provider'] == 'openai':

        return openai.TTS(voice=voice_data['voice_type'],speed=voice_data['speed'])
    
    elif voice_data["voice_provider"] == 'deepgram':

        return deepgram.TTS(model=voice_data['voice_type'])
    
    

async def entrypoint(ctx: JobContext):
    logger.info(f"connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    participant = await ctx.wait_for_participant()
    logger.info(f"starting voice assistant for participant {participant.identity}")

    



    if "sip.trunkPhoneNumber" in participant.attributes:

        logger.info(f"Caller phone number is {participant.attributes['sip.trunkPhoneNumber']}")
        # agent_metadata =  await get_metadata_by_number(participant.attributes['sip.trunkPhoneNumber'])
        userID = load_user_id_by_phone_number(participant.attributes['sip.trunkPhoneNumber'])

    else:

        userID = participant.attributes['chatbot_id']
        # logger.info(f"this is chabotId------>   {participant.attributes['chatbot_id']}")

    
    voice_data = await Singelton_db.get_data_from_supabase(userID)
    
    message = voice_data['prompt']
    
    initial_ctx = llm.ChatContext().append(
        role="system",
        text=message,
    )

    # userID = load_user_id_by_phone_number(participant.attributes['sip.trunkPhoneNumber'])

    

    async def truncate_context(assistant: VoicePipelineAgent,chat_ctx: llm.ChatContext):
        
        logger.info("this the zeroth index ------>",chat_ctx.messages[0].content)
        logger.info("this is index number -1 ------>",chat_ctx.messages[-1].content)

        result = await get_prompt(chat_ctx.messages[0].content,chat_ctx.messages[-1].content,userID,voice_data)

        if result == 'error':

            chat_ctx.messages[-1].content = voice_data['error_message']

        else:

            chat_ctx.messages[0].content = result
        

        end = time.time()
        logger.info("TOTAL TIME TAKEN",end-sstart)


        if len(chat_ctx.messages) > 15:
            chat_ctx.messages = chat_ctx.messages[-15:]

       

    fnc_ctx = AssistantFnc()
    # Wait for the first participant to connect
    participant = await ctx.wait_for_participant()

    assistant = VoicePipelineAgent(
        vad=ctx.proc.userdata["vad"],
        stt=deepgram.STT(),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=await switchProvider(voice_data),
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
