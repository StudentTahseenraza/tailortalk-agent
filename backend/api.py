from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.agent import process_user_input
import traceback

app = FastAPI(title="TailorTalk API")

class ChatRequest(BaseModel):
    input: str

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        print(f"➡️ Received input: {request.input}")
        response = process_user_input(request.input)
        print(f"✅ Response generated: {response}")
        return {"response": response}
    except Exception as e:
        print(f"❌ Error in /chat: {str(e)}")
        traceback.print_exc()  # 🔍 Shows detailed error trace
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
