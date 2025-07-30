
import asyncio
import datetime
from typing import Any, Optional


async def execute_command(command: str, cwd: Optional[str] = None, timeout: int = 30) -> dict[str, Any]:
    """Execute a bash command and return the result."""
    try:
        # Create subprocess
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
            shell=True,
        )

        # Wait for command to complete with timeout
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            return {
                "success": False,
                "error": f"Command timed out after {timeout} seconds",
                "stdout": "",
                "stderr": "",
                "code": -1,
                "command": command,
                "executedAt": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }

        # Decode output
        stdout_str = stdout.decode('utf-8', errors='replace') if stdout else ""
        stderr_str = stderr.decode('utf-8', errors='replace') if stderr else ""

        return {
            "success": process.returncode == 0,
            "stdout": stdout_str,
            "stderr": stderr_str,
            "code": process.returncode,
            "command": command,
            "executedAt": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "stdout": "",
            "stderr": "",
            "code": -1,
            "command": command,
            "executedAt": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }

