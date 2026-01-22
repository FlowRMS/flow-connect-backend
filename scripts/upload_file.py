import argparse
import asyncio
import json
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).parent.parent))

from token_generator import generate_token

GRAPHQL_ENDPOINTS = {
    "local": "http://localhost:8006/graphql",
    "dev": "https://development.api.flowrms.com/graphql",
    "staging": "https://staging.v6.api.flowrms.com/graphql",
    "prod": "https://api.flowrms.com/graphql",
}

UPLOAD_FILE_MUTATION = """
mutation UploadFile($input: FileUploadInput!) {
    uploadFile(input: $input) {
        id
        fileName
        filePath
        fileSize
        fileType
        fileSha
        createdAt
    }
}
"""


async def upload_file(
    file_path: str,
    tenant: str,
    env: str,
    role: str,
    folder_id: str | None = None,
    folder_path: str | None = None,
    custom_file_name: str | None = None,
) -> dict:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    token = await generate_token(tenant_name=tenant, env=env, role=role)

    file_name = custom_file_name or path.name

    variables: dict = {
        "input": {
            "file": None,
            "fileName": file_name,
        }
    }

    if folder_id:
        variables["input"]["folderId"] = folder_id
    if folder_path:
        variables["input"]["folderPath"] = folder_path

    operations = json.dumps({
        "query": UPLOAD_FILE_MUTATION,
        "variables": variables,
    })

    file_map = json.dumps({"0": ["variables.input.file"]})

    graphql_url = GRAPHQL_ENDPOINTS.get(env, GRAPHQL_ENDPOINTS["dev"])

    async with httpx.AsyncClient(timeout=60.0) as client:
        with path.open("rb") as f:
            files = {
                "operations": (None, operations),
                "map": (None, file_map),
                "0": (file_name, f, "application/octet-stream"),
            }

            response = await client.post(
                graphql_url,
                files=files,
                headers={
                    "Authorization": f"Bearer {token}",
                    "X-Auth-Provider": "WORKOS",
                },
            )

    _ = response.raise_for_status()
    result = response.json()

    if "errors" in result:
        raise RuntimeError(f"GraphQL errors: {json.dumps(result['errors'], indent=2)}")

    return result["data"]["uploadFile"]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Upload a file using the GraphQL uploadFile mutation"
    )
    _ = parser.add_argument(
        "--file_path",
        type=str,
        help="Path to the file to upload",
    )
    _ = parser.add_argument(
        "--tenant",
        type=str,
        required=True,
        help="Tenant name",
    )
    _ = parser.add_argument(
        "--env",
        type=str,
        default="prod",
        help="Environment (local, dev, staging, prod)",
    )
    _ = parser.add_argument(
        "--role",
        type=str,
        default="admin",
        help="User role",
    )
    _ = parser.add_argument(
        "--folder-id",
        type=str,
        default=None,
        help="Target folder ID (UUID)",
    )
    _ = parser.add_argument(
        "--folder-path",
        type=str,
        default=None,
        help="Target folder path",
    )
    _ = parser.add_argument(
        "--file-name",
        type=str,
        default=None,
        help="Custom file name (defaults to original filename)",
    )

    args = parser.parse_args()

    result = asyncio.run(
        upload_file(
            file_path=args.file_path,
            tenant=args.tenant,
            env=args.env,
            role=args.role,
            folder_id=args.folder_id,
            folder_path=args.folder_path,
            custom_file_name=args.file_name,
        )
    )

    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    import dotenv
    _ = dotenv.load_dotenv()
    main()
# python scripts/upload_file.py --file_path /path/to/document.pdf --tenant demosupport --env staging