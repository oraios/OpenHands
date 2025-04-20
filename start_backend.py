import uvicorn

# Global variables for host and port
HOST = "127.0.0.1"
PORT = 3000

if __name__ == "__main__":
    print(f"Starting server on {HOST}:{PORT}.")
    uvicorn.run(
        "openhands.server.listen:app",
        host=HOST,
        port=PORT,
        reload=True,
        reload_excludes=["./workspace"]
    )
