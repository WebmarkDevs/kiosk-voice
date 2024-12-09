from asyncio import Task
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from livekit import api
import os
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from requests.auth import HTTPBasicAuth
# Load environment variables
load_dotenv(dotenv_path=".env.local")
from apiHelper import *
# FastAPI app instance
app = FastAPI()
class PhoneNumberRequest(BaseModel):
    phone_number: str
    userID: str
    agent_welcome_message: Optional[str] = 'Hey, how can I help you today?'
    agent_prompts: Optional[str] =  "You are a helpful, respectful, and a honest chat assistant"
# Environment variables
LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TRUNK_SID = os.getenv("TRUNK_SID")
# Define a path for the JSON file
USER_PHONE_MAPPING_FILE = "user_phone_mapping.json"
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # List of allowed origins. Use ["*"] to allow all.
    allow_credentials=True,  # Whether to allow cookies and credentials
    allow_methods=["*"],  # List of HTTP methods to allow (e.g., GET, POST). Use ["*"] to allow all.
    allow_headers=["*"],  # List of HTTP headers to allow. Use ["*"] to allow all.
)

# Utility function to save userID and phone number
def save_user_phone_mapping(phone_number: str, user_id: str):
    """Save phone number and userID mapping to a JSON file."""
    try:
        
        # Load existing data if file exists
        try:
            with open(USER_PHONE_MAPPING_FILE, "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {}
        
        # Add or update the mapping
        data[phone_number] = user_id
        
        # Save back to the file
        with open(USER_PHONE_MAPPING_FILE, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving mapping: {str(e)}")
def get_phone_number_sid(phone_number: str):
    """Fetch the Phone Number SID from Twilio API."""
    url = f"https://api.twilio.com/2010-04-01/Accounts/{ACCOUNT_SID}/IncomingPhoneNumbers.json"
    params = {"PhoneNumber": phone_number}

    # Make the request
    response = requests.get(url, params=params, auth=HTTPBasicAuth(ACCOUNT_SID, AUTH_TOKEN))
    if response.status_code == 200:
        phone_numbers = response.json().get("incoming_phone_numbers", [])
        if phone_numbers:
            return phone_numbers[0]["sid"]
        raise HTTPException(status_code=404, detail="Phone number SID not found")
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

@app.post("/create-phone-number-agent")
async def create_phone_number_agent(request: PhoneNumberRequest):
    """Add a phone number to a Twilio trunk and create a SIP trunk."""
    # Validate Twilio credentials
    if not ACCOUNT_SID or not AUTH_TOKEN:
        raise HTTPException(status_code=500, detail="Twilio credentials not found in environment variables")
        
    try:
        
        await remove_dispatch_and_trunk(request.userID)
        # Step 1: Add Phone Number to Twilio Trunk
        phone_number_sid = get_phone_number_sid(request.phone_number)
        url_twilio = f"https://trunking.twilio.com/v1/Trunks/{TRUNK_SID}/PhoneNumbers"
        data_twilio = {"PhoneNumberSid": phone_number_sid}
        response_twilio = requests.post(url_twilio, data=data_twilio, auth=HTTPBasicAuth(ACCOUNT_SID, AUTH_TOKEN))
        
        if response_twilio.status_code != 201:
            raise HTTPException(status_code=response_twilio.status_code, detail=response_twilio.text)

        # Step 2: Create SIP Trunk in LiveKit
        token_response = get_livekit_token(identity="default-identity", name="Auto-Retry", room="default-room")
        token = token_response.get("token")
        url_livekit = f"https://{LIVEKIT_URL.replace('wss://', '')}/twirp/livekit.SIP/CreateSIPInboundTrunk"
        headers_livekit = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload_livekit = {
            "trunk": {
                "name": request.userID,
                "numbers": [request.phone_number],
                "metadata": str({
                    "userID": request.userID,
                    "agent_welcome_message": request.agent_welcome_message,
                    "agent_prompts": request.agent_prompts
                    })
            }
            
        }
        response_livekit = requests.post(url_livekit, headers=headers_livekit, json=payload_livekit)
        response_livekit.raise_for_status()  # Check for HTTP errors
        
        # Extract necessary data
        sip_trunk_id = response_livekit.json().get('sip_trunk_id')
        metadata = response_livekit.json().get('metadata')
        url_livekit = f"https://{LIVEKIT_URL.replace('wss://', '')}/twirp/livekit.SIP/CreateSIPDispatchRule"
        headers_livekit = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload_livekit = {
            "name": request.userID,
            "trunk_ids": [sip_trunk_id],
            "rule": {
            "dispatchRuleIndividual": {
                "roomPrefix": "call"
            },
            "metadata": str({
                "userID": request.userID
            })
            }
        }
        response_livekit = requests.post(url_livekit, headers=headers_livekit, json=payload_livekit)
        response_livekit.raise_for_status()  # Check for HTTP errors
        save_user_phone_mapping(request.phone_number, request.userID)
        # Return combined response
        return {
            "message": "Phone number added to Twilio trunk and SIP trunk created successfully",
            "twilio_details": response_twilio.json(),
            "sip_trunk_id": sip_trunk_id,
            "dispatch" : response_livekit.json(),
            "metadata" : metadata
        }
    
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"HTTP error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.post("/gettoken")
def get_livekit_token(identity: str, name: str, room: str):
    """Generate a LiveKit token with Video and SIP grants."""
    try:
        token = api.AccessToken(
            LIVEKIT_API_KEY,
            LIVEKIT_API_SECRET
        ).with_identity(identity) \
         .with_name(name) \
         .with_grants(api.VideoGrants(
             room_join=True,
             room=room
         )).with_sip_grants(api.SIPGrants(
             admin=True,
             call=True
         )).to_jwt()
        return {"token": token}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token generation failed: {str(e)}")


@app.get("/fetch-sip-trunks")
def fetch_sip_trunks():
    """Fetch SIP trunks and handle token regeneration if needed."""
    try:
        # Generate a token for SIP trunk request
        token_response = get_livekit_token(
            identity="default-identity",
            name="Auto-Retry",
            room="default-room"
        )
        token = token_response.get("token")

        # Prepare API request
        url = f"https://{LIVEKIT_URL.replace('wss://', '')}/twirp/livekit.SIP/ListSIPInboundTrunk"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # Make the request to fetch SIP trunks
        response = requests.post(url, headers=headers, json={})
        response.raise_for_status()  # Check for HTTP errors
        return response.json()  # Return the response JSON if successful
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch SIP trunks: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )


# Run the FastAPI app on port 3002
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=3003,reload=True)
