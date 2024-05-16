from fastapi import FastAPI, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import subprocess
from threading import Timer
import signal

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models_dir = '../text-generation-webui/models'

servers = []

check_servers = False


def run_server_check():
    global check_servers
    if check_servers:
        Timer(10.0, run_server_check).start()
        for p in servers:
            if p['process'].poll() is not None:
                servers.remove(p)
                print(f"Server {p['name']} is not running. Removed from list")
    else:
        print("Server check stopped")


@app.get("/models")
def get_models():
    global models_dir
    return os.listdir(models_dir)


def run_command(command: str):
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return process
    except Exception as e:
        print(f"Failed to start server: {str(e)}")
        return None


@app.post("/start-server/")
async def start_server(model_name: str = 'vicuna-7b-v1.5-16k.Q6_K.gguf', n_ctx: int = 16384, port: int = 8080):
    command = f'../llama.cpp/server -m {models_dir}/{model_name} -c {n_ctx} -ngl 50  --host 0.0.0.0 --port {port}'

    global servers
    global check_servers
    # Check if there is a server already running on same port

    #  run 'sudo lsof -n -i :8080 | grep LISTEN' to check if port is already in use
    out = run_command(f'sudo lsof -n -i :{port} | grep LISTEN').stdout.read()
    if out:
        raise HTTPException(status_code=400, detail=f"Port {port} is already in use")

    server_process = run_command(command)
    servers.append({"name": model_name, "port": port, "process": server_process})

    if server_process is None:
        raise HTTPException(status_code=500, detail=f"Failed to start server")

    if not check_servers:
        check_servers = True
        run_server_check()

    return {"message": "Server started successfully", "pid": server_process.pid}


@app.get("/running-servers")
async def running_servers():
    global servers

    return [{**p, "process": p["process"].pid} for p in servers]


@app.post("/stop-server")
async def stop_server(pid: int = None):
    global servers
    global check_servers

    if pid is not None:
        server_process = next((p['process'] for p in servers if p['process'].pid == pid), None)
    else:
        raise HTTPException(status_code=400, detail="Please provide either pid ")

    if server_process is None:
        raise HTTPException(status_code=400, detail="Please provide a valid pid ")
    port = next((p['port'] for p in servers if p['process'].pid == server_process.pid), None)


    print(f"stopping server: {server_process.pid}")

    if server_process is None or server_process.poll() is not None:
        raise HTTPException(status_code=400, detail="Server is not running")

    try:
        # Send Ctrl-C to the running process to stop it
        run_command(f'sudo kill -9 {server_process.pid}')
        run_command(f'sudo kill -9 $(sudo lsof -t -i:{port})')
        servers = [p for p in servers if p['process'].pid != server_process.pid]
        return {"message": "Server stopped successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop server. Error: {str(e)}")
