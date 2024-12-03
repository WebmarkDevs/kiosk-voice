import asyncio
import json
from uuid import uuid4
from venv import logger
import aiohttp
from typing import Annotated, List, Optional

from composio_openai import ComposioToolSet
from livekit.agents import llm
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.agents.multimodal import MultimodalAgent
from enum import Enum
from typing import Annotated, List, Optional
from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,Function
)
# Define EventType Enum
class EventType(str, Enum):
    default = "default"
    outOfOffice = "outOfOffice"
    focusTime = "focusTime"
    workingLocation = "workingLocation"
FUNCTION_CALL_PROMPT = "The function {function_name} has been called, and its result is:\n{result}. Please process this result and provide an appropriate, user-friendly response for the assistant."
FUNCTION_CALL_RETURN_ERROR_PROMPT = "Sorry but something went wrong, please try again or make another request"
toolset = ComposioToolSet()
# Define EventType Enum
class EventType(str, Enum):
    default = "default"
    outOfOffice = "outOfOffice"
    focusTime = "focusTime"
    workingLocation = "workingLocation"
def convert_event_to_tool_call(event_data: dict, function_name: str) -> ChatCompletionMessageToolCall:
    # Serialize event_data to JSON
    arguments_json = json.dumps(event_data)
    
    # Create the tool call structure
    tool_call = ChatCompletionMessageToolCall(
        id=str(uuid4()),  # Generate a unique ID for the tool call
        function=Function(arguments=arguments_json, name=function_name),
        type="function"
    )
    return tool_call
class AssistantFnc(llm.FunctionContext):

    @llm.ai_callable()
    async def GOOGLECALENDAR_CREATE_EVENT(
        self,
        userID: Annotated[
            str, llm.TypeInfo(description="User ID")
        ],
        start_datetime: Annotated[
            str, llm.TypeInfo(description="Start date and time of the event.")
        ],
        event_duration: Annotated[
            str, llm.TypeInfo(description="Duration of the meeting event, e.g., '3h30m', '2h', '20m'.")
        ],
        description: Annotated[
            Optional[str], llm.TypeInfo(description="Description of the event. Can contain HTML. Optional.")
        ] = None,
        eventType: Annotated[
            EventType, llm.TypeInfo(description="Type of the event, immutable post-creation.")
        ] = EventType.default,
        recurrence: Annotated[
            Optional[list[str]],
            llm.TypeInfo(description="List of recurrence rules for the event.")
        ] = None,
        timezone: Annotated[
            Optional[str], llm.TypeInfo(description="Timezone of the event. Example: 'America/New_York'.")
        ] = None,
        guests_can_modify: Annotated[
            bool, llm.TypeInfo(description="Indicates whether guests can modify the event.")
        ] = False,
        attendees: Annotated[
            Optional[list[str]],
            llm.TypeInfo(description="List of emails of attendees for the event.")
        ] = None,
        send_updates: Annotated[
            Optional[bool], llm.TypeInfo(description="Whether to send updates to the attendees.")
        ] = None,
        calendar_id: Annotated[
            str, llm.TypeInfo(description="The ID of the Google Calendar. `primary` for interacting with the primary calendar.")
        ] = "primary",
    ):
        """GOOGLECALENDAR_CREATE_EVENT"""
        # Ensure eventType is an EventType instance
        if isinstance(eventType, str):
            try:
                eventType = EventType(eventType)
            except ValueError:
                raise ValueError(f"Invalid eventType: {eventType}. Must be one of {[e.value for e in EventType]}")
        
        logger.info(f"Creating an event in the calendar {calendar_id}")
        function_name = 'GOOGLECALENDAR_CREATE_EVENT'
        # Prepare event data
        event_data = {
            "start_datetime": start_datetime,
            "event_duration": event_duration,
            "description": description,
            "eventType": eventType.value,
            "recurrence": recurrence,
            "timezone": timezone,
            "guests_can_modify": guests_can_modify,
            "attendees": attendees,
            "send_updates": send_updates,
            "calendar_id": calendar_id,
        }
        try:
            
            tool_call = convert_event_to_tool_call(event_data, function_name=function_name)
            result = await asyncio.to_thread(toolset.execute_tool_call, tool_call=tool_call, entity_id=userID)
            content = FUNCTION_CALL_PROMPT.format(function_name=function_name, result=str(result))
            logger.debug(f"""Event data: {event_data}
                            Content: {content}
                         """)
            return content
        except Exception as e : return FUNCTION_CALL_RETURN_ERROR_PROMPT
            
        #return {"status": "success", "event_data": event_data}
        