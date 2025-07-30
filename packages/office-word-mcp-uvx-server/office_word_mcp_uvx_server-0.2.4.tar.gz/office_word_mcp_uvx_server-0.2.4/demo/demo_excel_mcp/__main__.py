import asyncio
import typer

from .server import run_sse, run_stdio, run_streamable_http

app = typer.Typer(help="office-word-mcp-uvx-server")

# @app.command()
# def sse():
#     """Start Excel MCP Server in SSE mode"""
#     print("Excel MCP Server - SSE mode")
#     print("----------------------")
#     print("Press Ctrl+C to exit")
#     try:
#         asyncio.run(run_sse())
#     except KeyboardInterrupt:
#         print("\nShutting down server...")
#     except Exception as e:
#         print(f"\nError: {e}")
#         import traceback
#         traceback.print_exc()
#     finally:
#         print("Service stopped.")

# @app.command()
# def streamable_http():
#     """Start office-word-mcp-uvx-server in streamable HTTP mode"""
#     print("office-word-mcp-uvx-server - Streamable HTTP mode")
#     print("---------------------------------------")
#     print("Press Ctrl+C to exit")
#     try:
#         asyncio.run(run_streamable_http())
#     except KeyboardInterrupt:
#         print("\nShutting down server...")
#     except Exception as e:
#         print(f"\nError: {e}")
#         import traceback
#         traceback.print_exc()
#     finally:
#         print("Service stopped.")

@app.command()
def stdio():
    """Start office-word-mcp-uvx-server in stdio mode"""
    print("office-word-mcp-uvx-server - Stdio mode")
    print("-----------------------------")
    print("Press Ctrl+C to exit")
    try:
        run_stdio()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Service stopped.")

if __name__ == "__main__":
    app() 