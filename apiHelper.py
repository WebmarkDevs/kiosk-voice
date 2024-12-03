import asyncio
import os
from typing import Optional
from dotenv import load_dotenv
from livekit import api
from pydantic import BaseModel
import requests
import ast
# Load environment variables
load_dotenv(dotenv_path=".env.local")
class agentMetadata(BaseModel):
    userID: str
    agent_welcome_message: Optional[str] = 'Hey, how can I help you today?'
    agent_prompts: Optional[str] =  "You are a helpful, respectful, and a honest chat assistant"
# Define constants
LIVEKIT_URL = os.getenv("LIVEKIT_URL")

# # Generate token
# token = api.AccessToken(
#     os.getenv('LIVEKIT_API_KEY'),
#     os.getenv('LIVEKIT_API_SECRET')
# ).with_identity("identity") \
#  .with_name("name") \
#  .with_grants(api.VideoGrants(
#     room_join=True,
#     room="my-room")) \
#  .with_sip_grants(api.SIPGrants(
#     admin=True,
#     call=True)).to_jwt()

# print(token)

async def get_dispatch_rules_by_name(name_filter):
    """Fetch SIP Dispatch Rules and filter by name."""
    lkapi = api.LiveKitAPI(
        url=LIVEKIT_URL
    )
    try:
        # Fetch all SIP Dispatch Rules
        res = await lkapi.sip.list_sip_dispatch_rule(api.ListSIPDispatchRuleRequest())

        # Filter items based on the given name
        filtered_items = [
            item for item in res.items if item.name == name_filter
        ]
        return filtered_items
    finally:
        await lkapi.aclose()
async def remove_dispatch_and_trunk(agentID):
    lkapi = api.LiveKitAPI(
        url=LIVEKIT_URL
    )
    try:
        filtered_rules = await get_dispatch_rules_by_name(agentID)
        # Fetch all SIP Dispatch Rules
        for item in filtered_rules:
            item.metadata
            print(f"ID: {item.sip_dispatch_rule_id}, Name: {item.name}, Trunk IDs: {item.trunk_ids}")
            await lkapi.sip.delete_sip_trunk(api.DeleteSIPTrunkRequest(sip_trunk_id=item.trunk_ids[0]))
            await lkapi.sip.delete_sip_dispatch_rule(api.DeleteSIPDispatchRuleRequest(sip_dispatch_rule_id=item.sip_dispatch_rule_id))
    finally:
        await lkapi.aclose()

async def get_metadata_by_number(number):
    lkapi = api.LiveKitAPI(
        url=LIVEKIT_URL
    )
    try:
        ListSIPInboundTrunk =  await lkapi.sip.list_sip_inbound_trunk(api.ListSIPInboundTrunkRequest())
        for item in ListSIPInboundTrunk.items :
            if item.numbers[0]==number :
                data = ast.literal_eval(item.metadata)
                phone_request = agentMetadata(**data)
                return phone_request
    finally:
        await lkapi.aclose()

        
# async def main():
#     agentID = "string"
#     await remove_dispatch_and_trunk(agentID)
#     # phone_request = await get_metadata_by_number('+14154633127')
#     # print(phone_request)
        

# # Run the async main function
# asyncio.run(main())
