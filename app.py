import httpx
import os

from typing import Any

from kubernetes import client, config
from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse

def is_running_in_kubernetes() -> str:
    """
    Checks if the application is running inside a Kubernetes pod
    by looking for common Kubernetes-injected environment variables.
    """
    return (
        "KUBERNETES_SERVICE_HOST" in os.environ and
        "KUBERNETES_SERVICE_PORT" in os.environ
    )


# Initialize FastMCP server
mcp = FastMCP("sscs", host="0.0.0.0")


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")


@mcp.tool()
async def get_cluster_application_data(cluster: str, application: str) -> str:
    """Get information for an application in a cluster.

    Args:
        cluster: The name of the cluster where the application is running
        application: The name of the application
    """
    v1 = client.CoreV1Api()
    result = v1.read_namespaced_config_map(f"context--{cluster}--{application}", "sscs")
    return result.data[f"{cluster}--{application}.txt"]


if is_running_in_kubernetes():
    config.load_incluster_config()
else:
    config.load_kube_config()

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="streamable-http")
