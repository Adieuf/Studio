from fastapi import FastAPI, Request, Response
import httpx

from .copilot_auth import CopilotAuthenticator
from .copilot_agent import CopilotAgent

app = FastAPI(title="Copilot Chat API")

auth = CopilotAuthenticator()
agent = CopilotAgent(auth)

DIRECT_LINE_BASE = "https://directline.botframework.com/v3/directline"


@app.get("/api/chat/directline/token")
async def get_direct_line_token() -> dict[str, str]:
    """Return a short-lived Direct Line token for Web Chat."""
    token = agent.get_direct_line_token()
    return {"token": token, "streamUrl": f"{DIRECT_LINE_BASE}/conversations"}


@app.api_route("/api/chat/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_direct_line(full_path: str, request: Request) -> Response:
    """Reverse proxy to the Direct Line service."""
    url = f"{DIRECT_LINE_BASE}/{full_path}"
    headers = dict(request.headers)
    headers["Host"] = "directline.botframework.com"

    async with httpx.AsyncClient() as client:
        resp = await client.request(
            request.method,
            url,
            headers=headers,
            content=await request.body(),
            params=request.query_params,
        )

    response_headers = {
        key: value
        for key, value in resp.headers.items()
        if key.lower() != "transfer-encoding"
    }
    return Response(
        content=resp.content, status_code=resp.status_code, headers=response_headers
    )
