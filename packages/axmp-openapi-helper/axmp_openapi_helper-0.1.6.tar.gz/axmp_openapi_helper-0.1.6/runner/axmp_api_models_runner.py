"""This module provides a runner for the AxmpAPIModels."""

import asyncio
import logging
import logging.config

from axmp_openapi_helper.openapi.axmp_api_models import AxmpOpenAPI
from axmp_openapi_helper.utils.converter import Converter

logging.config.fileConfig("logging.conf", disable_existing_loggers=False)
logging.getLogger("axmp_openapi_helper.openapi.multi_openapi_helper").setLevel(
    logging.INFO
)
logging.getLogger("axmp_openapi_helper.openapi.axmp_api_models").setLevel(logging.INFO)
logging.getLogger("axmp_openapi_helper.openapi.operation").setLevel(logging.INFO)
logging.getLogger("axmp_openapi_helper.openapi.fastapi.fastapi_models").setLevel(
    logging.DEBUG
)
logger = logging.getLogger("appLogger")
logger.setLevel(logging.DEBUG)


async def main():
    """Run the axmp api models."""
    axmp_open_api = AxmpOpenAPI.from_spec_file(
        file_path="runner/openapi/zcp/zcp_alert_backend_openapi_spec.json"
    )
    # axmp_open_api = AxmpOpenAPI.from_spec_string(
    #     spec_string=xx # swagger_json of backend-server
    # )
    # axmp_open_api = AxmpOpenAPI.from_openapi(
    #     openapi=xx # OpenAPI model using the swagger_json of backend-server
    # )

    operations = axmp_open_api.get_operations_by_tag_method_pattern(
        tags=["alert", "channel"], methods=["post"], regex=r"^/api/alert/v1/.*"
    )

    tools = Converter.operations_to_tools(
        server_name="zcp_alert_backend",
        base_path="/api/alert/v1",
        axmp_open_api=axmp_open_api,
        operations=operations,
    )

    # print the tools
    for tool in tools:
        print("-" * 100)
        # print(f"server_name: {tool.server_name}")
        print(f"tool_name: {tool.name}")
        # print(f"tool_description: {tool.description}")
        print(f"tool_path: {tool.path}")
        print(f"tool_method: {tool.method}")
        # print(f"tool_query_params: {tool.query_params}")
        # print(f"tool_path_params: {tool.path_params}")
        # print(f"tool_request_body: {tool.request_body}")


if __name__ == "__main__":
    asyncio.run(main())
