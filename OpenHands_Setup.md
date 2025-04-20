# Making OpenHands Run

Instructions or running Serena locally inside OpenHands. The MCP support there
was [merged just on 10.04.2025](https://github.com/All-Hands-AI/OpenHands/pull/7637) 
and is not part of the official documentation or the
last released docker image at the time of writing. Nevertheless, it works!

## Config

After cloning with

```shell
git clone git@github.com:All-Hands-AI/OpenHands.git
```

we need to configure OpenHands before we begin.

```shell
cp config.template.toml config.toml
```

There add mcp config and modify sandbox config to setup a volume mount for your code

```toml
[core]
...
workspace_base = "/my/repo"
workspace_mount_path_in_sandbox = "/workspace"
workspace_mount_path = "/my/repo"

[mcp]
mcp_servers = ["http://localhost:8000/sse"]
```

You can set the runtime to `local`, which will run shell commands directly on the host.
However, it does not mean things will be fast... The runtime is recreated unnecessarily, see
https://github.com/All-Hands-AI/OpenHands/issues/7962


Also disable all `codeact_*` settings

```toml
[agent]
enable_browsing = false
enable_llm_editor = false
enable_editor = false
enable_jupyter = false
enable_cmd = false
enable_think = false
enable_finish = false

```

Also disable the default in context prompt

```toml
[llm]
in_context_learning_example=""
```

## Installation

Install frontend dependencies and build the frontend

```shell
cd frontend
npm install
npm run build
```

Now for backend

```shell
mamba create -n openhands python=3.12
mamba activate openhands   
mamba install conda-forge::nodejs    
mamba install conda-forge::poetry
```

Since openhands uses poetry, and it doesn't go hand in hand with mamba, you need to force
poetry to install into the active env if you want things to work without `poetry run`
(note that `poetry shell` no longer works, and `poetry env activate` didn't work as one would expect).

So:

```shell
poetry config virtualenvs.create false
poetry install --no-root
```

After that you can set the setting back to true (the default) if you want
```shell
poetry config virtualenvs.create true
```

## Start Serena in SSE Mode

Run

```shell
uv run --directory /path/to/serena serena-mcp-server --transport sse /path/to/project.yml
```

## Start Backend

The docs from the readme don't exactly work, but you can start the backend
and frontend separately.

For the backend, you can do

```shell
make start-backend
```

which is equivalent to 

```shell
poetry run uvicorn openhands.server.listen:app --host "127.0.0.1" --port 3000 --reload --reload-exclude "./workspace"
```

Since this is not debuggable, you may prefer to start it through a python script.

```python
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
        # not sure it does anything, this directory does not exist and is also not created 
        # or mounted in the startup process
        reload_excludes=["./workspace"]
    ) 
```

For some unholy reason, the frontend needs to be built for the backend to startup,
see installation section

## Start Frontend

The make command works

```shell
make start-frontend
```

which is the same as 

```shell
cd frontend
export VITE_BACKEND_HOST="127.0.0.1:3000" 
export VITE_FRONTEND_PORT=3001
npm run dev -- --port 3001 --host "127.0.0.1"
```

When the frontend opens, go to settings, select your model and enter your api key.

> IMPORTANT: the pro version of Gemini may cost far more than the experimental one, 
> make sure to not accidentally select it!

## First Conversation

### In Docker Mode

On your first conversation, OpenHands will build a docker image and start a container.
**This is very slow!** You will see the message 

`================ DOCKER BUILD STARTED ================`

in the backend logs, just be patient. Eventually, you will get a response.

Ask the LLM to list the available tools, you will see Serena mcp tools (the names are postfixed with `_mcp_tool_call`).

### In Local Mode

You can run OpenHands in local mode