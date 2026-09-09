# Manufacturing Quality Intelligence deployment

The quality-intelligence API runs on Render and its static decision workspace runs on Vercel. The copilot has a deterministic fallback and does not require a key.

1. Create a Render Blueprint from this repository. Keep the service name `manufacturing-quality-intelligence-api`; Render starts `mqi.service.api:app` and checks `/health`.
2. Confirm `https://manufacturing-quality-intelligence-api.onrender.com/health` is healthy.
3. Import the repository in Vercel and set Root Directory to `src/mqi/service/static`. Do not override the checked-in `vercel.json`.
4. Open the Vercel URL, run the quality analysis, inspect the model evidence, and ask the copilot a process question.
5. Optional: add `GEMINI_API_KEY` only as a Render secret.

The API bridge is in `src/mqi/service/static/config.js`; update it if the Render service is renamed.
