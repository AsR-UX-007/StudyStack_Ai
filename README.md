# StudyStack AI — Supabase Login + Google Gemini

This update keeps the existing StudyStack AI HTML/CSS/JavaScript interface and FastAPI/Gemini backend, and adds:

- Email/password account creation and sign-in through Supabase Auth
- Google sign-in through Supabase Auth
- Greeting based on local time: Good morning / afternoon / evening + the signed-in student's name
- Cloud-saved tasks separated by Supabase user ID, with Row Level Security
- Sign out
- Gemini API key stays on the server in Render environment variables

## 1. Create a Supabase project

1. Open https://supabase.com/dashboard and create a project.
2. In Project Settings → API, copy the **Project URL** and the **anon/public key** (or publishable key if your project uses that naming).
3. Never put the Supabase `service_role` key in the frontend or Render's `SUPABASE_ANON_KEY` variable.

## 2. Create the task table

In Supabase → SQL Editor → New query, paste and run the contents of `supabase/schema.sql`. This creates `student_data` and Row Level Security policies so a signed-in user can read/write only their own task row.

## 3. Enable email/password authentication

In Supabase → Authentication → Providers, make sure Email is enabled. For quick testing you can turn off email confirmation in Authentication settings; for a public app, keep email confirmation enabled and configure SMTP if you need reliable confirmation email delivery.

## 4. Enable Google sign-in

1. Supabase → Authentication → Providers → Google → enable it.
2. Create OAuth credentials in Google Cloud Console (OAuth client ID, Web application).
3. Add the Supabase callback URL shown by Supabase to the Google OAuth client's **Authorized redirect URIs**.
4. Put the Google Client ID and Client Secret into Supabase's Google provider settings.
5. In Supabase → Authentication → URL Configuration, set **Site URL** to your Render public URL, e.g. `https://YOUR-SERVICE.onrender.com`.
6. Add that same URL to the allowed **Redirect URLs** list. If you use a custom domain, add it too.

## 5. Configure Render

In Render → your StudyStack AI service → Environment, add these variables:

- `GEMINI_API_KEY` = your existing Google Gemini API key
- `GEMINI_MODEL` = the model name you successfully tested, e.g. `gemini-3.6-flash`
- `SUPABASE_URL` = your Supabase Project URL
- `SUPABASE_ANON_KEY` = your Supabase anon/public or publishable key

Do not set `SUPABASE_ANON_KEY` to a service-role key. The anon/public key is designed to be visible in the browser; the database must be protected by the supplied RLS policies.

## 6. Deploy

Commit the updated `index.html`, `main.py`, `render.yaml`, `README.md`, and `supabase/schema.sql` to your GitHub repository. Render should redeploy automatically, or use Manual Deploy → Deploy latest commit.

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

## 7. Test

1. Open your Render URL. You should see the login page.
2. Create an account using email/password and complete email confirmation if enabled.
3. Add a task, sign out, then create/sign in with another account. The second account should not see the first account's tasks.
4. Sign in with Google after Google provider setup.
5. Reload the page: tasks should load from Supabase.
6. Check `/api/health` for Gemini status and test the AI Assistant.

## Security notes

- Never commit `.env`, Gemini keys, Google OAuth client secrets, or Supabase service-role keys.
- The frontend only receives the Supabase anon/public key. RLS is essential and is enabled in `supabase/schema.sql`.
- This version stores the task list as one JSON row per user to keep the existing UI code mostly unchanged. A larger production app may use a normalized tasks table and additional rate limits/monitoring.
- Google sign-in will not work until the Google OAuth client and Supabase provider are configured correctly.
