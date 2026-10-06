#!/usr/bin/env python3
"""
APIVault Unified Development Startup Script.

Launches both the FastAPI backend (port 8000) and Vite frontend (port 5173)
development servers concurrently with a single command, streams prefixed logs,
and cleanly terminates all child processes on exit.

Usage:
    python start.py              # Starts both backend and frontend
    python start.py --backend    # Starts backend only
    python start.py --frontend   # Starts frontend only
"""

import argparse
import atexit
import os
import platform
import shutil
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"

_procs: list[tuple[subprocess.Popen, str]] = []
_cleaned_up = False


def stream_output(pipe, prefix: str):
    """Streams lines from a subprocess pipe with a formatted prefix."""
    try:
        for line in iter(pipe.readline, ""):
            if not line:
                break
            print(f"[{prefix}] {line.rstrip()}", flush=True)
    except Exception:
        pass
    finally:
        try:
            pipe.close()
        except Exception:
            pass


def cleanup():
    """Safely terminates all spawned child processes and their process trees."""
    global _cleaned_up
    if _cleaned_up:
        return
    _cleaned_up = True

    had_procs = bool(_procs)
    for proc, name in _procs:
        if proc and proc.poll() is None:
            print(f"[start.py] Stopping {name} (PID: {proc.pid})...", flush=True)
            if platform.system() == "Windows":
                try:
                    subprocess.run(
                        ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        check=False,
                    )
                except Exception:
                    proc.kill()
            else:
                proc.terminate()
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    proc.kill()
    if had_procs:
        print("[start.py] All development servers stopped.", flush=True)



def signal_handler(signum, frame):
    """Handles termination signals gracefully."""
    print("\n[start.py] Received shutdown signal...", flush=True)
    cleanup()
    sys.exit(0)


# Register exit and signal handlers
atexit.register(cleanup)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
if hasattr(signal, "SIGBREAK"):
    signal.signal(signal.SIGBREAK, signal_handler)


def main():
    parser = argparse.ArgumentParser(
        description="APIVault Unified Development Startup Script"
    )
    parser.add_argument(
        "--backend", action="store_true", help="Start backend server only"
    )
    parser.add_argument(
        "--frontend", action="store_true", help="Start frontend server only"
    )
    parser.add_argument(
        "--port-backend",
        type=int,
        default=8000,
        help="Backend port (default: 8000)",
    )
    args = parser.parse_args()

    start_backend = True
    start_frontend = True
    if args.backend and not args.frontend:
        start_frontend = False
    elif args.frontend and not args.backend:
        start_backend = False

    npm_cmd = "npm.cmd" if platform.system() == "Windows" else "npm"
    if start_frontend and not shutil.which(npm_cmd) and not shutil.which("npm"):
        print(f"Error: '{npm_cmd}' not found in PATH. Please install Node.js.")
        sys.exit(1)

    print("=" * 64)
    print("  APIVault - Development Server Startup")
    print("=" * 64)
    if start_backend:
        print(f"  * Backend:   http://127.0.0.1:{args.port_backend}")
        print(f"    - Docs:    http://127.0.0.1:{args.port_backend}/docs")
        print(f"    - Health:  http://127.0.0.1:{args.port_backend}/api/health")
    if start_frontend:
        print("  * Frontend:  http://localhost:5173")
    print("=" * 64)
    print("  Press Ctrl+C to shut down all servers.\n")

    threads = []

    try:
        # Start Backend Server
        if start_backend:
            backend_cmd = [
                sys.executable,
                "-m",
                "uvicorn",
                "app.main:app",
                "--reload",
                "--host",
                "127.0.0.1",
                "--port",
                str(args.port_backend),
            ]
            backend_proc = subprocess.Popen(
                backend_cmd,
                cwd=str(BACKEND_DIR),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            _procs.append((backend_proc, "Backend"))
            t_backend = threading.Thread(
                target=stream_output,
                args=(backend_proc.stdout, "backend"),
                daemon=True,
            )
            t_backend.start()
            threads.append(t_backend)

        # Start Frontend Server
        if start_frontend:
            frontend_cmd = [npm_cmd, "run", "dev"]
            frontend_proc = subprocess.Popen(
                frontend_cmd,
                cwd=str(FRONTEND_DIR),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            _procs.append((frontend_proc, "Frontend"))
            t_frontend = threading.Thread(
                target=stream_output,
                args=(frontend_proc.stdout, "frontend"),
                daemon=True,
            )
            t_frontend.start()
            threads.append(t_frontend)

        # Watch child processes
        while True:
            time.sleep(0.5)
            for proc, name in _procs:
                if proc.poll() is not None:
                    print(f"\n[start.py] {name} process exited.", flush=True)
                    cleanup()
                    return

    except KeyboardInterrupt:
        print("\n[start.py] Shutting down development servers...", flush=True)
        cleanup()


if __name__ == "__main__":
    main()
