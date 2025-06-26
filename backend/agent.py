from typing import Dict, TypedDict, Optional
from langgraph.graph import StateGraph, END
import google.generativeai as genai
from backend.calendar_utils import check_availability, book_appointment
import os
import re
import dateutil.parser
from datetime import datetime, timedelta
import json
import time

# Initialize Gemini API
try:
    genai.configure(api_key="YOUR GEMINI_API_KEY")
    model = genai.GenerativeModel("models/gemini-2.5-flash-lite-preview-06-17")
except Exception as e:
    print(f"Failed to initialize Gemini API: {str(e)}")
    raise

# Define state
class AgentState(TypedDict):
    user_input: str
    intent: str
    date: Optional[str]
    time_range: Optional[Dict[str, str]]
    available_slots: Optional[list]
    selected_slot: Optional[str]
    response: str

# Prompts
intent_prompt = """
Analyze the user's input and determine their intent. Possible intents:
- 'schedule': User wants to book an appointment.
- 'check_availability': User wants to know available time slots.
- 'confirm': User is confirming a time slot.
- 'unknown': Intent is unclear.

Extract date (YYYY-MM-DD or relative like 'tomorrow') and time_range if provided.

User input: {input}

Return a JSON object (no markdown, no code blocks, just the JSON string):
{{
    "intent": "schedule|check_availability|confirm|unknown",
    "date": "YYYY-MM-DD or relative date",
    "time_range": {{"start": "HH:MM", "end": "HH:MM"}} or null,
    "selected_slot": "HH:MM" or null
}}
"""


response_prompt = """
You are TailorTalk, a friendly AI assistant for booking appointments. Respond naturally based on the state, guiding the user toward booking. List available slots clearly if provided. If confirming, confirm the booking details. If intent is unclear, ask for clarification.

Current state: {state}

Response:
"""

# Nodes
def detect_intent(state: AgentState) -> AgentState:
    prompt = intent_prompt.format(input=state["user_input"])
    retries = 3

    for attempt in range(retries):
        try:
            response = model.generate_content(prompt)
            result = response.text.strip()
            print(f"\n🧠 Gemini raw response (attempt {attempt + 1}):\n{result}")

            # ✨ Remove code block markers if present
            if result.startswith("```json"):
                result = result.replace("```json", "").replace("```", "").strip()

            # ✨ Parse directly if it's a valid JSON string
            parsed = json.loads(result)

            # ✅ Safely extract values
            state["intent"] = parsed.get("intent", "unknown")
            state["date"] = parsed.get("date")
            state["time_range"] = parsed.get("time_range")
            state["selected_slot"] = parsed.get("selected_slot")
            return state

        except Exception as e:
            print(f"❌ Error in detect_intent (attempt {attempt + 1}): {str(e)}")
            if attempt == retries - 1:
                state["intent"] = "unknown"
                state["response"] = "Sorry, I couldn't understand your request. Could you try rephrasing?"
            time.sleep(1)
    return state



def check_slots(state: AgentState) -> AgentState:
    if state["intent"] in ["schedule", "check_availability"]:
        try:
            slots = check_availability(state["date"], state["time_range"])
            state["available_slots"] = slots
            if slots:
                state["response"] = f"Available slots on {state['date']}: {', '.join(slots)}. Please choose one."
            else:
                state["response"] = f"No slots available on {state['date']}. Try another date or time range."
        except ValueError as e:
            state["response"] = f"Invalid date or time format: {str(e)}. Please specify the date (e.g., 'tomorrow' or '2025-06-27') and optionally a time range (e.g., '3-5 PM')."
    return state

def confirm_booking(state: AgentState) -> AgentState:
    if state["intent"] == "confirm" and state["selected_slot"]:
        try:
            result = book_appointment(state["date"], state["selected_slot"])
            state["response"] = result
        except Exception as e:
            state["response"] = f"Failed to book appointment: {str(e)}. Please try again."
    elif state["intent"] == "confirm":
        state["response"] = "Please specify a time slot to confirm (e.g., '13:30')."
    return state

def generate_response(state: AgentState) -> AgentState:
    if not state.get("response"):
        prompt = response_prompt.format(state=json.dumps(state, indent=2))
        try:
            response = model.generate_content(prompt)
            state["response"] = response.text.strip()
        except Exception as e:
            print(f"Error in generate_response: {str(e)}")
            state["response"] = "Sorry, I'm having trouble responding. Please try again."
    return state

# Build workflow
workflow = StateGraph(AgentState)
workflow.add_node("detect_intent", detect_intent)
workflow.add_node("check_slots", check_slots)
workflow.add_node("confirm_booking", confirm_booking)
workflow.add_node("generate_response", generate_response)

workflow.set_entry_point("detect_intent")
workflow.add_conditional_edges(
    "detect_intent",
    lambda state: "check_slots" if state["intent"] in ["schedule", "check_availability"] else "confirm_booking" if state["intent"] == "confirm" else "generate_response"
)
workflow.add_edge("check_slots", "generate_response")
workflow.add_edge("confirm_booking", "generate_response")
workflow.add_edge("generate_response", END)

graph = workflow.compile()

def process_user_input(user_input: str) -> str:
    state = {"user_input": user_input}
    result = graph.invoke(state)
    return result["response"]