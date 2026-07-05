import uvicorn
import json
import base64
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from hr_agent import get_agent


app = FastAPI(
    title="AI Recruitment Assistant",
    description="API for resume analysis and job recommendations powered by an AI Agent",
    version="1.0.0",
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Check the server health status."""
    return {"status": "ok", "message": "The system is running normally"}


@app.post("/find_jobs")
async def find_jobs(resume: UploadFile = File(...)):
    """
    Receive a resume (PDF), analyze it, and search for matching jobs.
    Return the results as Server-Sent Events (SSE) for real-time progress updates.
    """
    # Read and encode the PDF file to Base64
    content = await resume.read()
    base64_pdf = base64.b64encode(content).decode("utf-8")
    file_size_kb = len(content) / 1024

    async def event_generator():
        agent = get_agent()
        print(f"Starting resume analysis: {resume.filename} ({file_size_kb:.1f} KB)")

        # Send a status message indicating the analysis has started
        yield f"data: {json.dumps({'type': 'status', 'content': 'Resume received. Starting analysis...'})}\n\n"

        # Build a multimodal message (text + file)
        msg_content = [
            {
                "type": "text",
                "text": "This is my resume. Please analyze it and find the most suitable job opportunities for me.",
            },
            {
                "type": "file",
                "base64": base64_pdf,
                "mime_type": "application/pdf",
                "filename": resume.filename,
            },
        ]

        # Stream the agent execution process
        async for chunk in agent.astream(
                {"messages": [{"role": "user", "content": msg_content}]},
                stream_mode="values",
        ):
            # Check the latest message in the conversation
            if "messages" in chunk:
                latest_message = chunk["messages"][-1]

                # 1. The agent decides to call a tool (job search)
                if hasattr(latest_message, "tool_calls") and latest_message.tool_calls:
                    for tool_call in latest_message.tool_calls:
                        tool_name = tool_call.get("name", "unknown")
                        yield f"data: {json.dumps({'type': 'status', 'content': f'Searching for jobs ({tool_name})...'})}\n\n"

                # 2. The tool returns its results
                elif latest_message.type == "tool":
                    yield f"data: {json.dumps({'type': 'status', 'content': 'Matching jobs found. Analyzing compatibility...'})}\n\n"

                # 3. Final response from the AI
                elif latest_message.type == "ai" and latest_message.content:
                    content = latest_message.content
                    yield f"data: {json.dumps({'type': 'result', 'content': content})}\n\n"

        # End the stream
        print(f"Resume analysis completed: {resume.filename}")
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


if __name__ == "__main__":
    uvicorn.run("hr_agent_be:app", host="0.0.0.0", port=8000, reload=True)