import json
import logging
from dotenv import load_dotenv
from fastapi import HTTPException
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    llm,
)
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import openai, deepgram, silero
import requests
from apiHelper import *
from helper.func_calling import AssistantFnc
load_dotenv(dotenv_path=".env.local")
logger = logging.getLogger("voice-agent")


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()
# Define a path for the JSON file
USER_PHONE_MAPPING_FILE = "user_phone_mapping.json"

def getdata_api(query,userID):
        url = f"https://dev-api.getkiosk.ai/search_pinecone"
        try:
            payload = json.dumps({
            "query_text": query,
            "namespace" : userID
            })
            headers = {
            'Content-Type': 'application/json'
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            logger.info(f""" #################################################################
                        {response}
                        {payload}
                        """)
            response_data = response.json()
            data = response_data.get("matches", "")
            return data
        except requests.exceptions.RequestException as e:
            
            print(f"Error occurred: {e}")
            return ''
def get_prompt( query,userID):
        data = getdata_api(query,userID)
        #self.save_to_json(data)
        logger.info(f"################### DATA {data}")
        prompt = f"""
        Context information is below.
        ---------------------
        {data}
        ---------------------
        User question: [{query}]
        --------------------- 
        Please follow these guidelines when responding to queries: 
        1. Answer the query concisely in few words based only on the given context information as a salesman . 
        2. Never mention that you have been trained on or lack context. 
        3. Only if someone greets you, respond with a greeting as the chat assistant for small business name. 
        4. Do not hallucinate or use any prior knowledge outside of the provided context information. 
        5. Answer All queries in markdown format only, for the anchor tags it should always render a link, do not render image tag links as anchor . 
        6. Use the history and the context to answer the current question only. 
        7. Please respond in a natural, conversational tone, avoiding phrases like "Based on the context provided." 
        8. Your responses should sound as if they are coming from a knowledgeable human rather than a bot. 
        9. Never try to answer the history, only answer the current question.
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

async def truncate_context(assistant: VoicePipelineAgent,chat_ctx: llm.ChatContext):
    
    userID = load_user_id_by_phone_number(assistant._participant.attributes['sip.trunkPhoneNumber'])
    chat_ctx.messages[0].content = get_prompt(chat_ctx.messages[0].content,userID)
    if len(chat_ctx.messages) > 15:
        chat_ctx.messages = chat_ctx.messages[-15:]
async def entrypoint(ctx: JobContext):
    logger.info(f"connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    participant = await ctx.wait_for_participant()
    logger.info(f"starting voice assistant for participant {participant.identity}")
    logger.info(f"Caller phone number is {participant.attributes['sip.trunkPhoneNumber']}")
    agent_metadata =  await get_metadata_by_number(participant.attributes['sip.trunkPhoneNumber'])

    initial_ctx = llm.ChatContext().append(
        role="system",
        text=(
            f"{agent_metadata.agent_prompts}"
            f"Use this information for calling functions that use UserID. UserID = {agent_metadata.userID}"
            "Do not provide userID to the user under any circumstances."
            "When a user wants to perform a function calling, help them generate relevant information, don't ask too many questions."
        ),
    )

    
    fnc_ctx = AssistantFnc()
    # Wait for the first participant to connect
    participant = await ctx.wait_for_participant()
    logger.info(f"starting voice assistant for participant {participant.identity}")
    logger.info(f"Caller phone number is {participant.attributes['sip.trunkPhoneNumber']}")
    assistant = VoicePipelineAgent(
        vad=ctx.proc.userdata["vad"],
        stt=deepgram.STT(),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=openai.TTS(),
        chat_ctx=initial_ctx,
        fnc_ctx=fnc_ctx,
        max_nested_fnc_calls=1,
        before_llm_cb=truncate_context
    )
    assistant.start(ctx.room, participant)

    await assistant.say(agent_metadata.agent_welcome_message, allow_interruptions=True)


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        ),
    )
