import asyncio
import json
import time
from datetime import datetime
from typing import List

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from routers import species

app = FastAPI(title="FaunaDataInc API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

active_connections: List[asyncio.Queue] = []

@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    if "/stream-logs" in request.url.path or "/monitor" in request.url.path:
        return await call_next(request)

    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    log_entry = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "method": request.method,
        "url": str(request.url.path),
        "client": request.client.host,
        "status": response.status_code,
        "latency": f"{process_time:.4f}s"
    }

    if active_connections:
        json_data = json.dumps(log_entry)
        for queue in active_connections:
            await queue.put(json_data)
            
    return response

async def event_generator(request: Request):
    queue = asyncio.Queue()
    active_connections.append(queue)
    try:
        while True:
            if await request.is_disconnected():
                break
                
            data = await queue.get()
            yield f"data: {data}\n\n"
    except asyncio.CancelledError:
        pass
    finally:
        active_connections.remove(queue)

@app.get("/stream-logs")
async def stream_logs(request: Request):
    return StreamingResponse(event_generator(request), media_type="text/event-stream")

@app.get("/monitor", response_class=HTMLResponse)
async def get_monitor():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>FaunaData Inc - Realtime Monitor</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background-color: #121212; color: #00ff00; font-family: 'Courier New', monospace; }
            .card { background-color: #1e1e1e; border: 1px solid #333; }
            .table { color: #e0e0e0; }
            .status-200 { color: #00ff00; }
            .status-404 { color: #ffca2c; }
            .status-500 { color: #ff0000; }
            .new-row { animation: flash 1s ease-out; }
            @keyframes flash {
                0% { background-color: #00ff00; color: #000; }
                100% { background-color: transparent; color: #e0e0e0; }
            }
        </style>
    </head>
    <body class="p-4">
        <div class="container">
            <h2 class="text-center mb-4">FaunaData Inc. | Monitor de Tráfico</h2>
            <div class="alert alert-dark text-center" id="status-bar">
                <span class="spinner-grow spinner-grow-sm text-success" role="status"></span>
                Conectado y esperando eventos...
            </div>
            
            <div class="card shadow">
                <div class="card-body">
                    <table class="table table-dark table-hover">
                        <thead>
                            <tr>
                                <th>Hora</th>
                                <th>IP</th>
                                <th>Método</th>
                                <th>Endpoint</th>
                                <th>Status</th>
                                <th>Latencia</th>
                            </tr>
                        </thead>
                        <tbody id="log-container">
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <script>
            const eventSource = new EventSource('/stream-logs');
            const container = document.getElementById('log-container');

            eventSource.onmessage = function(event) {
                const log = JSON.parse(event.data);
                
                const row = document.createElement('tr');
                row.classList.add('new-row'); // Animación de flash
                
                let statusColor = 'text-white';
                if(log.status == 200) statusColor = 'status-200';
                if(log.status == 404) statusColor = 'status-404';
                if(log.status >= 500) statusColor = 'status-500';

                row.innerHTML = `
                    <td>${log.timestamp}</td>
                    <td>${log.client}</td>
                    <td><span class="badge bg-secondary">${log.method}</span></td>
                    <td class="fw-bold">${log.url}</td>
                    <td class="${statusColor} fw-bold">${log.status}</td>
                    <td>${log.latency}</td>
                `;
                
                // Insertar al principio de la tabla
                container.prepend(row);
                
                if(container.children.length > 20) {
                    container.removeChild(container.lastChild);
                }
            };

            eventSource.onerror = function() {
                document.getElementById('status-bar').innerHTML = 
                    '<span class="text-danger">⚠️ Conexión perdida. Reconectando...</span>';
            };
        </script>
    </body>
    </html>
    """
    return html_content

app.include_router(species.router)