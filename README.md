# StudyStack AI — Gemini API edition

## Run on Mac
1. Create a key at https://aistudio.google.com/apikey.
2. In Terminal, enter the project folder and run:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Set the key without displaying it:
   ```bash
   read -s "GEMINI_API_KEY?Paste your Gemini API key: "
   echo
   export GEMINI_API_KEY
   ```
   Paste with Command+V, then press Enter.
4. Start the app:
   ```bash
   export GEMINI_MODEL="gemini-2.5-flash"
   uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```
5. Check http://127.0.0.1:8000/api/health, then open http://127.0.0.1:8000.

If requests fail, check Terminal for `Gemini request failed:`. Free quota and model availability depend on the account/project; see https://aistudio.google.com/.

## Online deployment
The included `render.yaml` configures Render. Add `GEMINI_API_KEY` and `GEMINI_MODEL` in Render's Environment settings. Never commit the key to GitHub or put it in frontend JavaScript.

The project stores tasks in browser local storage; there is no central database, authentication, or rate limiting.
