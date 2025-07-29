"""
Entry point for running agentlin modules as executables.
Usage:
  python -m agentlin.tools.server.bash_mcp_server --port 9999
  agentlin --mcp-server bash --port 9999
"""
import typer
from agentlin.tools.server.bash_mcp_server import mcp as bash_mcp_server
from agentlin.tools.server.file_system_mcp_server import mcp as file_system_mcp_server
from agentlin.tools.server.memory_mcp_server import mcp as memory_mcp_server

app = typer.Typer()

mcp_servers = {
    "bash": bash_mcp_server,
    "file_system": file_system_mcp_server,
    "memory": memory_mcp_server,
}

@app.command()
def launch(
    mcp_server: str = typer.Option("bash", help="The name of the MCP server to run. Choices: [bash, file_system, memory]"),
    host: str = typer.Option("localhost", help="The host to bind the server to"),
    port: int = typer.Option(9999, help="The port to run the server on"),
    path: str = typer.Option("bash_mcp", help="The path for the MCP server"),
    debug: bool = typer.Option(False, help="Enable debug mode"),
):
    if mcp_server not in mcp_servers:
        typer.echo(f"Unknown MCP server: {mcp_server}. Available servers: {', '.join(mcp_servers.keys())}")
        raise typer.Exit(code=1)
    mcp = mcp_servers[mcp_server]
    typer.echo(f"Starting {mcp_server} MCP server on {host}:{port} at path {path} with debug={debug}")
    # Run the selected MCP server
    mcp.run("http", host=host, port=port, path=path, log_level="debug" if debug else "info")




if __name__ == "__main__":
    app()