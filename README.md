
> [!WARNING]
> 
> This is __vybeware__ (I'm going to assume I made that word up.) Vybeware is software that's entirely vybe-coded by prompting an LLM to do practically all the coding, with me only supervising decision making on the pipeline, doing logic debugging, and a few miscellaneous tasks I didn't want to leave to the coin-tosser (LLM).
> 
> Therefore, just because the software works, it doesn't mean it's **safe**. I haven't scoured the codebase to catch zero days, API leaks, etc. So if you use this project, don't store anything that you don't want a hacker (or the general public) finding.

# LLM Inference Proxy

I made this to run on docker as a container. It's a Python 3.12 FastAPI application with a password-gated plain HTML/CSS/JavaScript inference workspace. It performs **non-streaming** LLM requests exclusively from the server. Browser storage is used only for local sign-in state and response history.

## Security boundaries

- `APP_PASSWORD`, `LLM_ENDPOINT_URL`, and `LLM_API_KEY` are loaded only by the FastAPI process from `.env`.
- The browser never receives the expected password, upstream URL, or API key.
- Login returns an opaque, short-lived bearer token; the browser keeps that token in `localStorage` for convenience.
- Every `/api/inference` request is authenticated again by the server.
- API errors are redacted. Do not place secrets in prompts or browser storage.

## Run locally

1. Copy `.env.example` to `.env` and replace `APP_PASSWORD`.
2. Create and activate a Python 3.12 virtual environment.
3. Install dependencies: `python -m pip install -r requirements.txt`.
4. Start the app: `python -m uvicorn app.main:app --reload`.
5. Open `http://127.0.0.1:8000`.

If `LLM_ENDPOINT_URL` is blank, the application provides a deterministic safe demo response. To call an upstream, configure an OpenAI-compatible chat-completions URL, `LLM_API_KEY` (when required), and `LLM_MODEL` in the server-side `.env`. The adapter sends `{ model, messages, stream: false }` and accepts standard `choices[0].message.content`, `text`, or `response` output formats.

### Azure OpenAI configuration

This application supports Azure OpenAI chat completions. Set these server-side values in `.env` (replace the placeholders; do not commit this file):

- `LLM_PROVIDER=azure_openai`
- `LLM_ENDPOINT_URL=https://<resource-name>.openai.azure.com/openai/deployments/<deployment-name>/chat/completions?api-version=2024-10-21`
- `LLM_API_KEY=<Azure OpenAI resource key>`

For Azure OpenAI, the deployment name belongs in `LLM_ENDPOINT_URL`; `LLM_MODEL` is ignored. The proxy sends the Azure-required `api-key` header and `{ messages, stream: false }`, so no token streaming is requested. Use the API version supported by the Azure OpenAI resource if it differs from the example.

For an Azure OpenAI or Foundry OpenAI **v1 base endpoint**, use:

- `LLM_PROVIDER=azure_openai_v1`
- `LLM_ENDPOINT_URL=https://<resource>.services.ai.azure.com/openai/v1`
- `LLM_API_KEY=<resource key>`
- `LLM_MODEL=<model or deployment name>`

The application turns that base URL into `/openai/v1/chat/completions`, supplies the `api-key` header, and sends `{ model, messages, stream: false }`. Do not set the v1 base URL as `openai_compatible`, because that sends a bearer header and posts to the incomplete base path.

## UI behavior

- `/` and `/workspace` serve the same single-page interface.
- The sign-in panel is shown until login succeeds.
- The `chapatiGPT` header, inference status, and log-out control share one line on desktop.
- A single compact search panel keeps the scrollable local responses above the prompt input. Prompts use green Markdown content and responses use blue Markdown content.
- **Use past responses** is enabled by default. It sends the latest 20 local prompt/response messages as context with the next inference request; clear the checkbox to send only the current prompt.
- Prompt and response lines support GitHub-flavored Markdown. Marked parses Markdown and DOMPurify sanitizes the resulting HTML before it is displayed.
- Send with **Ctrl+Enter**. The input starts at two lines and grows up to ten lines, then scrolls vertically.
- **Log out** removes only the browser session. **Clear** removes only the local response history.

## API

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/health` | Reports `demo` or `configured` without revealing configuration. |
| POST | `/api/auth/login` | Validates `{ "password": "…" }`. |
| POST | `/api/inference` | Authenticated inference for `{ "prompt": "…" }`. |

All failures have `{ "error": { "code", "message", "details" } }` shape. Send `Authorization: Bearer <token>` for inference.

## Test and container run

Run tests with `python -m pytest`.

For Docker, first create `.env`, then use `docker compose up --build`. Docker Compose requires a local `.env`; it is deliberately ignored by Git.

## Limits and next steps

Sessions are in-memory and therefore expire on restart. This scaffold has no database or migrations, by design; responses remain local to each browser. Add rate limiting, HTTPS, and a durable session store before using shared access beyond a trusted environment.
