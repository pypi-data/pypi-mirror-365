import base64
import os
import sys
import logging
import json
from typing import Any, Dict, Optional, List
import httpx
import xml.etree.ElementTree as ET
from flask import Flask, request, jsonify
import asyncio

# --- Configuration ---
SERVICENOW_INSTANCE = os.environ.get("SERVICENOW_INSTANCE")
SERVICENOW_USER = os.environ.get("SERVICENOW_USER")
SERVICENOW_PASSWORD = os.environ.get("SERVICENOW_PASSWORD")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# --- Flask App Initialization ---
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,  # Log to stdout for web server environments
)
logger = logging.getLogger(__name__)


# --- Gemini AI Integration ---
class GeminiProcessor:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required for GeminiProcessor.")
        self.api_key = api_key
        logger.info("GeminiProcessor initialized.")

    async def process_catalog_request(self, user_request: str) -> Dict[str, Any]:
        prompt = f"""
		          You are a ServiceNow expert. Analyze the user's request and extract the necessary information to create a catalog item.
		          Return ONLY a valid JSON object with the following fields.
		          - If a value isn't present in the request, use "NEEDS_VALIDATION".
		          - All values must be strings.
		          
		          JSON structure:
		          {{
		            "name": "Item Name",
		            "short_description": "A brief description.",
		            "description": "A detailed description.",
		            "category": "Software, Hardware, or Service",
		            "price": "Price as a number, e.g., '25.50'",
		            "fulfillment_group": "The team responsible for fulfillment.",
		            "vendor": "The vendor of the item, if any."
		          }}
		          
		          User Request: "{user_request}"
		          """

        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        headers = {"Content-Type": "application/json"}
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={self.api_key}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, json=payload, headers=headers, timeout=60.0
                )
                response.raise_for_status()
                result = response.json()

                if "candidates" in result and result["candidates"]:
                    content = result["candidates"][0]["content"]["parts"][0]["text"]
                    json_str = (
                        content.strip()
                        .replace("```json", "")
                        .replace("```", "")
                        .strip()
                    )
                    logger.info(f"Received from Gemini: {json_str}")
                    return json.loads(json_str)
                else:
                    logger.error("No candidates returned from Gemini.")
                    return {}
        except (httpx.HTTPStatusError, json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error processing request with Gemini: {e}")
            return {}


# --- ServiceNow API Client ---
class ServiceNowClient:
    def __init__(self, instance_url: str, username: str, password: str):
        if not instance_url or "your-instance" in instance_url:
            raise ValueError("ServiceNow instance URL is not configured.")
        self.base_url = f"{instance_url}/api/now/table"

        auth_string = f"{username}:{password}"
        auth_bytes = auth_string.encode("ascii")
        base64_bytes = base64.b64encode(auth_bytes)
        base64_string = base64_bytes.decode("ascii")

        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Basic {base64_string}",
        }
        self.client = httpx.AsyncClient(headers=self.headers, timeout=30.0)

    async def _request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Helper method to make requests to the ServiceNow API."""
        try:
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            if response.status_code == 204:  # No Content for DELETE
                return {"status": "success", "message": "Record deleted successfully."}
            return response.json()
        except httpx.HTTPStatusError as e:
            error_details = e.response.json() if e.response.content else {}
            logger.error(
                f"HTTP Error: {e.response.status_code} - {e.request.url} - Details: {error_details}"
            )
            return {"error": {"message": str(e), "details": error_details}}
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return {"error": {"message": f"An unexpected error occurred: {str(e)}"}}

    async def get_records(self, table_name: str, query: str) -> Dict[str, Any]:
        url = f"{self.base_url}/{table_name}?sysparm_query={query}"
        return await self._request("GET", url)

    async def create_record(
        self, table_name: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/{table_name}"
        return await self._request("POST", url, json=data)

    async def update_record(
        self, table_name: str, sys_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/{table_name}/{sys_id}"
        return await self._request("PATCH", url, json=data)

    async def get_sys_id(
        self, table_name: str, field_name: str, field_value: str
    ) -> Optional[str]:
        query = f"{field_name}={field_value}"
        response = await self.get_records(table_name, query)
        if response and response.get("result") and len(response["result"]) > 0:
            return response["result"][0].get("sys_id")
        return None


# --- Core Agent Logic ---
async def agent_workflow(user_request: str) -> str:
    """
    The core logic of the agent, refactored to be callable from an API endpoint.
    """
    if not GEMINI_API_KEY:
        return "Error: Gemini API key is not configured on the server."

    client = ServiceNowClient(SERVICENOW_INSTANCE, SERVICENOW_USER, SERVICENOW_PASSWORD)
    gemini = GeminiProcessor(GEMINI_API_KEY)

    item_details = await gemini.process_catalog_request(user_request)
    if (
        not item_details
        or not item_details.get("name")
        or item_details.get("name") == "NEEDS_VALIDATION"
    ):
        return "Error: Could not understand the request. Please provide a name for the catalog item."

    # --- Data Validation Step ---
    group_name = item_details.get("fulfillment_group")
    if group_name and group_name != "NEEDS_VALIDATION":
        group_sys_id = await client.get_sys_id("sys_user_group", "name", group_name)
        if not group_sys_id:
            return f"Validation Error: The fulfillment group '{group_name}' does not exist in ServiceNow."
        item_details["fulfillment_group"] = group_sys_id

    category_name = item_details.get("category")
    if category_name and category_name != "NEEDS_VALIDATION":
        category_sys_id = await client.get_sys_id("sc_category", "title", category_name)
        if not category_sys_id:
            return f"Validation Error: The category '{category_name}' does not exist."
        item_details["category"] = category_sys_id

    vendor_name = item_details.get("vendor")
    if vendor_name and vendor_name != "NEEDS_VALIDATION":
        vendor_sys_id = await client.get_sys_id("core_company", "name", vendor_name)
        if not vendor_sys_id:
            return f"Validation Error: The vendor '{vendor_name}' does not exist."
        item_details["vendor"] = vendor_sys_id

    # --- Duplicate Check Step ---
    query = f"name={item_details['name']}"
    existing_records = await client.get_records("sc_cat_item", query)
    if existing_records.get("error"):
        return f"ServiceNow API Error: {existing_records['error']['message']}"

    # --- Create or Update Logic ---
    if existing_records.get("result"):
        sys_id = existing_records["result"][0]["sys_id"]
        update_payload = {
            k: v
            for k, v in item_details.items()
            if k != "name" and v != "NEEDS_VALIDATION"
        }

        response = await client.update_record("sc_cat_item", sys_id, update_payload)
        if "error" in response:
            return f"Error updating record: {response['error']['message']}"
        return f"Successfully updated existing catalog item '{item_details['name']}' (Sys ID: {sys_id})."
    else:
        create_payload = {
            k: v for k, v in item_details.items() if v != "NEEDS_VALIDATION"
        }
        response = await client.create_record("sc_cat_item", create_payload)
        if "error" in response:
            return f"Error creating record: {response['error']['message']}"
        new_sys_id = response.get("result", {}).get("sys_id")
        return f"Successfully created new catalog item '{item_details['name']}' (Sys ID: {new_sys_id})."


# --- Flask API Endpoint ---
@app.route("/manage_item", methods=["POST"])
async def manage_item_endpoint():
    """
    This is the endpoint that ServiceNow Virtual Agent will call.
    It expects a JSON payload with a "user_request" key.
    """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    user_request = data.get("user_request")

    if not user_request:
        return jsonify({"error": "Missing 'user_request' in payload"}), 400

    try:
        # Since Flask routes are synchronous, we run the async workflow in an event loop
        result = await agent_workflow(user_request)
        return jsonify({"response": result})
    except Exception as e:
        logger.error(f"An error occurred in the agent workflow: {e}")
        return jsonify({"error": "An internal server error occurred."}), 500


# # --- Main Execution Block ---
# if __name__ == "__main__":
#     # To run this server:
#     # 1. Make sure you have Flask installed: pip install Flask
#     # 2. Run the script: python your_server_file.py
#     # The server will be accessible at http://127.0.0.1:5000
#     app.run(host="0.0.0.0", port=5000, debug=True)
import click


@click.command()
@click.option("--host", default="0.0.0.0", help="Host to bind to.")
@click.option("--port", default=5000, help="Port to listen on.")
def main(host, port):
    """Runs the ServiceNow Catalog Agent server."""
    logger.info(f"Starting server on {host}:{port}")
    app.run(host=host, port=port)
