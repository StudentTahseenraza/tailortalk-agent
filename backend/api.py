from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.agent import process_user_input
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import traceback

app = FastAPI(title="TailorTalk API")

# ✅ Allow your deployed frontend to access this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ai-news-platform-ulc8rmqwtyd7pzs8hwra5z.streamlit.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# ✅ Redirect backend root to frontend
@app.get("/")
def redirect_to_frontend():
    return RedirectResponse("https://ai-news-platform-ulc8rmqwtyd7pzs8hwra5z.streamlit.app")
