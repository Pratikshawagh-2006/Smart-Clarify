# Smart-Clarify

## AI chatbot setup
1. Get a free key at https://aistudio.google.com/apikey and add `GEMINI_API_KEY=...` to `.env` (see `.env.example`). Never commit `.env`.
2. Add the new column to the existing database (create_all does not alter old tables):
   `ALTER TABLE questions ADD COLUMN ai_answer TEXT NULL;`
3. `pip install -r requirements.txt` then `uvicorn main:app --reload`
4. Test `POST /student/chat` in Swagger at http://127.0.0.1:8000/docs

Routing: Gemini answers -> status `auto_resolved`. Gemini unsure / needs teacher / API error -> status `escalated` (teacher queue).
