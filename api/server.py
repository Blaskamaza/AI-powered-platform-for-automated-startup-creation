"""
AI Factory API Server
FastAPI backend for integrating Python agents with React Dashboard.
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "agents"))

from agents.cpo import CPO
from agents.tech_lead import TechLead
from agents.cmo import CMO
from agents.sales_head import SalesHead
from agents.qa_lead import QALead
from agents.perplexity_suite import PerplexitySuite
from agents.config import BASE_DIR, PUBLIC_DATA_DIR

# === Models ===
class FactoryRequest(BaseModel):
    idea: str
    context: str = "Uzbekistan Market"
    mode: str = "auto"  # "auto" or "manual"

class ArtifactUpdate(BaseModel):
    content: str

class ScanRequest(BaseModel):
    topic: str = "Uzbekistan business opportunities"
    region: str = "CIS"

# === WebSocket Manager ===
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# === Lifespan ===
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 AI Factory API started")
    yield
    print("🛑 AI Factory API stopped")

# === App ===
app = FastAPI(
    title="AI Factory API",
    description="Backend for UZ AI Factory Dashboard",
    version="1.0.0",
    lifespan=lifespan
)

# CORS: Environment-based origins
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000,http://localhost:8000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Include Routers ===
from api.board import router as board_router
app.include_router(board_router)

# Agent Runner API
from services.agent_runner import create_agent_api_router
agent_router = create_agent_api_router()
app.include_router(agent_router)

# === Helper ===
PROJECTS_DIR = BASE_DIR / "data" / "projects"

def get_project_folders() -> List[str]:
    """Get list of all project folders."""
    if not PROJECTS_DIR.exists():
        return []
    return [f.name for f in PROJECTS_DIR.iterdir() if f.is_dir()]

def get_project_artifacts(project_name: str) -> Dict[str, str]:
    """Get all artifacts for a project."""
    project_path = PROJECTS_DIR / project_name
    if not project_path.exists():
        return {}
    
    artifacts = {}
    for file in project_path.glob("*.md"):
        artifacts[file.stem] = file.read_text(encoding="utf-8")
    for file in project_path.glob("*.json"):
        artifacts[file.stem] = file.read_text(encoding="utf-8")
    return artifacts

# === Routes ===
@app.get("/")
async def root():
    return {"status": "ok", "message": "AI Factory API v1.0"}

@app.get("/api/projects")
async def list_projects():
    """List all projects."""
    projects = get_project_folders()
    return {"projects": projects}

@app.get("/api/projects/{project_name}")
async def get_project(project_name: str):
    """Get project details and artifacts."""
    artifacts = get_project_artifacts(project_name)
    if not artifacts:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"name": project_name, "artifacts": artifacts}

@app.put("/api/projects/{project_name}/{artifact_name}")
async def update_artifact(project_name: str, artifact_name: str, update: ArtifactUpdate):
    """Update an artifact file."""
    project_path = PROJECTS_DIR / project_name
    if not project_path.exists():
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Try .md first, then .json
    file_path = project_path / f"{artifact_name}.md"
    if not file_path.exists():
        file_path = project_path / f"{artifact_name}.json"
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    file_path.write_text(update.content, encoding="utf-8")
    return {"status": "updated", "artifact": artifact_name}

@app.post("/api/factory/run")
async def run_factory(request: FactoryRequest):
    """Start the AI Factory pipeline (synchronous version)."""
    # For now, return immediately and let WebSocket handle streaming
    return {
        "status": "started",
        "idea": request.idea,
        "mode": request.mode,
        "message": "Connect to WebSocket for live updates"
    }

# === Intelligence API ===
@app.post("/api/intelligence/scan")
async def run_intelligence_scan(request: ScanRequest):
    """Run Perplexity Suite to find pains and trends."""
    try:
        suite = PerplexitySuite()
        
        # Run full scan in thread pool
        results = await asyncio.to_thread(
            suite.full_scan, request.topic, request.region
        )
        
        # Save results to cache
        cache_path = PUBLIC_DATA_DIR / "latest_scan.json"
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        return {
            "status": "success",
            "pains": results.get("pains", []),
            "trends": results.get("trends", []),
            "ideas": results.get("ideas", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/intelligence/pains")
async def get_cached_pains():
    """Get the latest cached pains from previous scan."""
    cache_path = PUBLIC_DATA_DIR / "latest_scan.json"
    if cache_path.exists():
        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {
            "pains": data.get("pains", []),
            "trends": data.get("trends", [])
        }
    return {"pains": [], "trends": []}

# === WebSocket ===
@app.websocket("/api/factory/ws")
async def factory_websocket(websocket: WebSocket):
    """WebSocket endpoint for streaming factory progress."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("action") == "start":
                idea = data.get("idea", "")
                context = data.get("context", "Uzbekistan Market")
                mode = data.get("mode", "auto")
                
                # Run factory in async manner
                await run_factory_async(idea, context, mode, websocket)
                
            elif data.get("action") == "approve":
                # For manual mode - signal to continue
                pass
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def run_factory_async(idea: str, context: str, mode: str, ws: WebSocket):
    """Run the factory pipeline with WebSocket streaming."""
    
    async def send(msg_type: str, content: str, phase: int = 0, data: dict = None):
        await ws.send_json({
            "type": msg_type,
            "content": content,
            "phase": phase,
            "data": data or {}
        })
    
    await send("start", f"👔 The Boss: Starting project for '{idea}'", 0)
    
    try:
        # Phase 1: CPO
        await send("phase", "🧠 PHASE 1: PRODUCT STRATEGY (CPO)", 1)
        await send("log", "🧠 CPO: Analyzing idea...", 1)
        
        cpo = CPO()
        prd = await asyncio.to_thread(cpo.create_prd, idea, context)
        
        if "error" in prd:
            await send("error", f"❌ CPO Error: {prd['error']}", 1)
            return
        
        project_name = prd.get("project_name", "unknown")
        await send("success", f"✅ PRD created for: {project_name}", 1, {"project_name": project_name})
        
        if mode == "manual":
            await send("pause", "⏸ Waiting for approval to continue...", 1)
            # Wait for approval message
            approval = await ws.receive_json()
            if approval.get("action") != "approve":
                return
        
        # Phase 2: Tech Lead
        await send("phase", "🏗 PHASE 2: ENGINEERING (Tech Lead)", 2)
        await send("log", "🏗 Tech Lead: Architecting solution...", 2)
        
        tech_lead = TechLead()
        prd_str = json.dumps(prd, indent=2)
        tech_spec = await asyncio.to_thread(tech_lead.create_spec, project_name, prd_str)
        
        if "error" in tech_spec:
            await send("error", f"❌ Tech Lead Error: {tech_spec['error']}", 2)
            return
        
        await send("success", "✅ Tech Spec created", 2)
        
        if mode == "manual":
            await send("pause", "⏸ Waiting for approval to continue...", 2)
            approval = await ws.receive_json()
            if approval.get("action") != "approve":
                return
        
        # Phase 3: CMO
        await send("phase", "📢 PHASE 3: MARKETING (CMO)", 3)
        await send("log", "📢 CMO: Crafting strategy...", 3)
        
        cmo = CMO()
        tech_spec_str = json.dumps(tech_spec, indent=2)
        marketing = await asyncio.to_thread(cmo.create_marketing_plan, project_name, tech_spec_str, context)
        
        if "error" in marketing:
            await send("error", f"❌ CMO Error: {marketing['error']}", 3)
            return
        
        await send("success", "✅ Marketing Plan created", 3)
        
        if mode == "manual":
            await send("pause", "⏸ Waiting for approval to continue...", 3)
            approval = await ws.receive_json()
            if approval.get("action") != "approve":
                return
        
        # Phase 4: Sales Head
        await send("phase", "💰 PHASE 4: SALES (Sales Head)", 4)
        await send("log", "💰 Sales Head: Building funnel...", 4)
        
        sales = SalesHead()
        marketing_str = json.dumps(marketing, indent=2)
        sales_kit = await asyncio.to_thread(sales.create_sales_kit, project_name, marketing_str, context)
        
        if "error" in sales_kit:
            await send("error", f"❌ Sales Head Error: {sales_kit['error']}", 4)
            return
        
        await send("success", "✅ Sales Kit created", 4)
        
        if mode == "manual":
            await send("pause", "⏸ Waiting for approval to continue...", 4)
            approval = await ws.receive_json()
            if approval.get("action") != "approve":
                return
        
        # Phase 5: QA Lead with Iteration Loop
        MAX_ITERATIONS = 3
        
        for attempt in range(1, MAX_ITERATIONS + 1):
            await send("phase", f"⚖️ PHASE 5: QUALITY CONTROL (QA Lead) - Attempt {attempt}/{MAX_ITERATIONS}", 5)
            await send("log", "⚖️ QA Lead: Auditing project...", 5)
            
            qa = QALead()
            qa_report = await asyncio.to_thread(qa.review_project, project_name)
            
            if "error" in qa_report:
                await send("error", f"❌ QA Lead Error: {qa_report['error']}", 5)
                return
            
            status = qa_report.get("status", "UNKNOWN")
            score = qa_report.get("score", 0)
            
            await send("log", f"📊 QA Report: {status} (Score: {score}/100)", 5)
            
            # Check if we pass
            if status == "PASS" or score >= 80:
                await send("success", f"✅ QA PASSED! Score: {score}/100", 5, {"phase": "qa_lead"})
                break
            
            elif status == "WARN" and score >= 60:
                await send("success", f"⚠️ QA WARN: Score: {score}/100 - Minor issues", 5, {"phase": "qa_lead"})
                break
            
            else:
                # FAIL - need to iterate
                if attempt < MAX_ITERATIONS:
                    await send("log", f"🔄 Iterating... Refining PRD based on QA feedback", 5)
                    
                    # Refine PRD
                    prd = await asyncio.to_thread(cpo.refine_prd, prd, qa_report)
                    
                    if "error" in prd:
                        await send("error", f"❌ Error refining PRD: {prd['error']}", 5)
                        return
                    
                    await send("log", "✅ PRD refined. Re-running downstream agents...", 5)
                    
                    # Re-run downstream agents
                    prd_str = json.dumps(prd, indent=2)
                    tech_spec = await asyncio.to_thread(tech_lead.create_spec, project_name, prd_str)
                    tech_spec_str = json.dumps(tech_spec, indent=2)
                    marketing = await asyncio.to_thread(cmo.create_marketing_plan, project_name, tech_spec_str, context)
                    marketing_str = json.dumps(marketing, indent=2)
                    sales_kit = await asyncio.to_thread(sales.create_sales_kit, project_name, marketing_str, context)
                    
                    await send("log", "✅ All agents re-ran. Proceeding to next QA check...", 5)
                else:
                    await send("error", f"❌ PROJECT REJECTED after {MAX_ITERATIONS} attempts. Score: {score}/100", 5)
                    return
        
        # Final
        await send("complete", f"🏁 Pipeline complete! Project: {project_name}", 6, {
            "project_name": project_name,
            "status": status,
            "score": score
        })
        
    except Exception as e:
        await send("error", f"❌ Fatal Error: {str(e)}", 0)

# === Static Files & SPA Fallback ===
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Serve React build (after running `npm run build`)
DIST_DIR = BASE_DIR / "dist"

# Check if build exists
if DIST_DIR.exists():
    # Serve static assets (JS, CSS, images)
    app.mount("/assets", StaticFiles(directory=DIST_DIR / "assets"), name="assets")
    
    # SPA fallback - serve index.html for all non-API routes
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # If path starts with /api, let it fall through to API routes
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API route not found")
        
        # Serve index.html for all other routes (SPA routing)
        index_path = DIST_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        raise HTTPException(status_code=404, detail="Frontend not built")
else:
    @app.get("/")
    async def no_build():
        return {
            "status": "dev",
            "message": "Run 'npm run build' to create production build, then restart server.",
            "api_docs": "/docs"
        }

# === Run ===
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
