📅 TailorTalk – AI Appointment Booking Assistant
TailorTalk is an AI-powered assistant that helps users schedule appointments using natural language. 
Built with FastAPI, Google Gemini API, Google Calendar, and a user-friendly Streamlit interface, 
TailorTalk understands your message, checks availability, and books appointments seamlessly.

🔗 Live Demo
🚀 Frontend (Streamlit): [TailorTalk UI](https://ai-news-platform-ulc8rmqwtyd7pzs8hwra5z.streamlit.app/)

⚙️ Backend (FastAPI): [TailorTalk API](https://tailortalk-agent.onrender.com)

🔧 Tech Stack
Frontend	Streamlit
Backend	FastAPI + Uvicorn
AI Engine	Google Gemini 2.5 (Free Tier)
Calendar	Google Calendar API
Hosting	Render (backend), Streamlit Cloud (UI)

🚀 Features
✅ Natural language appointment booking (e.g. “Schedule a call tomorrow at 3 PM”)

✅ Gemini-powered intent detection

✅ Available slot suggestion

✅ Google Calendar integration

✅ Fully deployed and accessible via web

🛠️ Local Setup Instructions
1. Clone the Repo
git clone https://github.com/your-username/tailortalk.git
cd tailortalk

3. Create a virtual environment and activate it
python -m venv venv
.\venv\Scripts\activate

4. Install dependencies
pip install -r requirements.txt
5. Add environment variable
You can set your Google Gemini API key as:
$env:GOOGLE_API_KEY="your-gemini-api-key"

5. Run Backend
uvicorn backend.api:app --reload --port 8001

7. Run Frontend
streamlit run app.py

✅ Deployment
Backend: Deployed to Render
Frontend: Deployed to Streamlit Cloud

🙌 Contributing
Open to feedback, issues, and PRs!
Feel free to fork, clone, and improve the project.

📬 Contact
Made with ❤️ by Tahseen Raza
