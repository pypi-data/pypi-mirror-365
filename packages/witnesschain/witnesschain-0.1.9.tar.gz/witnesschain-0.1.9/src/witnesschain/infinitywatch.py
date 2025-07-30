
import asyncio
import aiohttp
import os
import base64
from urllib.parse import urlparse, unquote
import aiohttp
from typing import AsyncGenerator, Any
import logging


from .constants import Constants, wtns_get_base_url, InfinitywatchEndpoints
from .datatypes import NodeType, InfinitywatchNodeResponse
from .exceptions import WTNS_Exception


logger = logging.getLogger(__name__)


class Infinitywatch:
    """Main class for interacting with the Infinitywatch API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    
    async def query(
        self, 
        prompt: str, 
        inputs: list[str] | None = None,
        models: list[str] | None = None,
        model_parameters: dict[str, Any] | None = None,
        retries: int = 3,
        timeout: float = 5.0   
    ) -> AsyncGenerator[InfinitywatchNodeResponse, None]:
        
        # validating prompt
        if not isinstance(prompt, str):
            raise WTNS_Exception(f"Prompt must be a string, got {type(prompt).__name__}")
        if len(prompt.strip()) == 0:
            raise WTNS_Exception("Prompt cannot be empty")
        
        # validating inputs
        if inputs is not None:
            if not isinstance(inputs, list):
                raise WTNS_Exception(f"Inputs must be a list of key value pairs; eg: [{'type': 'image', 'value': 'image_url'}], got {type(inputs).__name__}")
            for item in inputs:
                if not isinstance(item, str):
                    raise WTNS_Exception(f"Each input item must be a string, got {type(item).__name__}")
            if len(inputs) == 0:
                inputs = None  # allow empty inputs
        
        # validating models
        if models is not None:
            if not isinstance(models, list):
                raise WTNS_Exception(f"Models must be a list of strings, got {type(models).__name__}")
            for model in models:
                if not isinstance(model, str):
                    raise WTNS_Exception(f"Each model name must be a string, got {type(model).__name__}")
                
        # validating model parameters
        if model_parameters is not None:
            if not isinstance(model_parameters, dict):
                raise WTNS_Exception(f"Model parameters must be a dictionary, got {type(model_parameters).__name__}")
            for key, value in model_parameters.items():
                if not isinstance(key, str):
                    raise WTNS_Exception(f"Model parameter keys must be strings, got {type(key).__name__}")
                if not isinstance(value, (str, int, float, bool)):
                    raise WTNS_Exception(f"Model parameter values must be strings, integers, floats or booleans, got {type(value).__name__}")
        else:
            model_parameters = {}
            
        processed_input = None
        if inputs is not None:
            processed_input = []
            for item in inputs:
                processed_input.append(
                    {"type": "image", "value": await _process_image(item)}
                )
        
        # defaulting inputs to empty list if Non
        
        # helper function to fetch a node, returns a node id or None if not found
        async def _fetch_node(model_name: str | None = None) -> str | None:
            payload = {
                "limit": 1,
                "in_a_challenge": False,
            }
            if model_name:
                payload["filter"] = {
                    "claims": {
                        "model": [ model_name ],
                    }
                }
            try:
                nodes = await _make_coordinator_call(self.api_key, InfinitywatchEndpoints.CHALLENGERS, payload)
                if nodes and 'challengers' in nodes and len(nodes['challengers']) > 0:
                    return nodes['challengers'][0]['id']
                else:
                   return None
            except WTNS_Exception as e:
                return None
        
        # helper functions to start a challenge on a given node id
        async def _start_challenge(node_id, prompt, inputs, model_parameters) -> str | None:
            payload = {                                             
                    "prover" : node_id,  
                    "challenge_input" : {
                        "prompt": prompt,
                        "input": inputs,
                        **model_parameters
                    },         
                    "num_challengers"       : 1        
                }
           
            try:
                challenge_response = await _make_coordinator_call(self.api_key, InfinitywatchEndpoints.CHALLENGE_REQUEST, payload)
                if challenge_response and 'challenge_id' in challenge_response :
                    return challenge_response['challenge_id']
                else:
                   return None
            except WTNS_Exception as e:
                return None
        
        # helper function to get the model response for a given challenge id
        async def _get_model_response(challenge_id: str) -> InfinitywatchNodeResponse:
            payload = {
                "challenge_id": challenge_id
            }
            model_response = None
            issues = None
            resp = {}
            while model_response is None: 
                try:
                    response = await _make_coordinator_call(self.api_key, InfinitywatchEndpoints.CHALLENGE_STATUS, payload)
                    resp = response
                    if response and 'state' in response:
                        if response['state'].startswith("ENDED"):
                            model_response = list(response['consolidated_result']['result'].keys())[0]
                        elif response['state'].startswith("ERR"):
                            model_response = None
                            issues = response['state']
                            break
                except WTNS_Exception as e:
                    issues = e.message
                await asyncio.sleep(5)  # wait before next check
                
            if model_response is None:
                model_response = issues or "No response received from the model"
            return InfinitywatchNodeResponse(
                node_id=resp.get('prover', {}).get('id', None),
                model_response=model_response,
                model=resp.get('prover', {}).get('claims', {}).get('model', None),
                challenge_id=challenge_id
            )
           
                
        # main logic to fetch nodes and start challenge and return the response
        async def _fetch_and_challenge_node(model_name) -> InfinitywatchNodeResponse:
            function_runs = -1
            challenge_id = None
            node_id = None
            while challenge_id is None and function_runs < retries:
                while node_id is None and function_runs <retries:
                    node_id = await _fetch_node(model_name)
                    if node_id is not None:
                        break
                    function_runs += 1
                    await asyncio.sleep(timeout)
                
                challenge_id = await _start_challenge(node_id, prompt, processed_input, model_parameters)
                if challenge_id is not None:
                    break
                function_runs += 1
                node_id = None
                await asyncio.sleep(timeout)
            
            if challenge_id is None:
                raise WTNS_Exception(f"Failed to query node with {model_name} after multiple retries..")
            
            model_response = await _get_model_response(challenge_id)
            return model_response
        
           
        tasks = [asyncio.create_task(_fetch_and_challenge_node(model)) for model in (models or [None])]
        
        # yield results out of task as soon as they are completed
        for task in asyncio.as_completed(tasks):
            response = await task
            yield response

       
async def _make_coordinator_call(api_key: str, endpoint: str,  payload: dict | None = None):
    headers = { 
        "Authorization": f"Bearer {api_key}"
    }
    
    url = wtns_get_base_url(Constants.PROOF_OF_MODEL) + endpoint
    
    payload = payload or {}
    
    async with aiohttp.ClientSession() as session:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, headers=headers, json=payload) as response:
                    try:
                        data = await response.json()
                    except aiohttp.ContentTypeError:
                        text = await response.text()
                        raise WTNS_Exception(f"Non-JSON response: {text}")

                    if response.status != 200:
                        error_msg = data.get("error", {}).get("message", "Unknown error")
                        raise WTNS_Exception(f"Status: {response.status} - {error_msg}")

                    return data.get("result")

            except aiohttp.ClientError as e:
                raise WTNS_Exception(f"Request failed: {str(e)}")       
            


async def _process_image(image: str) -> str:
    
    parsed = urlparse(image)

    # 1) Data URI
    if parsed.scheme == "data":
        logger.info("Detected image as base64-encoded data URI.")
        try:
            header, b64data = image.split(",", 1)
            # Validate base64 payload
            base64.b64decode(b64data)
            return b64data
        except Exception:
            raise ValueError("Invalid data URI or base64 payload.")

    # 2) HTTP/HTTPS URL
    if parsed.scheme in ("http", "https"):
        logger.info("Detected image as URL.")
        async with aiohttp.ClientSession() as session:
            async with session.get(image) as resp:
                if resp.status != 200:
                    raise ValueError(f"Failed to fetch image, status code {resp.status}")
                data = await resp.read()
        return base64.b64encode(data).decode("utf-8")

    # 3) file:// URL
    if parsed.scheme == "file":
        logger.info("Detected image as local file path (file://).")
        path = unquote(parsed.path)
        if not os.path.isfile(path):
            raise ValueError(f"File not found: {path}")
        with open(path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode("utf-8")

    # 4) plain local file path
    if os.path.isfile(image):
        logger.info("Detected image as local file path.")
        with open(image, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode("utf-8")

    # 5) parse anyways as raw base64 string
    b64str = image.strip()
    # Add padding if missing
    padding = len(b64str) % 4
    if padding:
        b64str += "=" * (4 - padding)
    try:
        base64.b64decode(b64str, validate=True)
        logger.info("Detected image as base64-encoded data URI.")
        return b64str
    except Exception:
        raise ValueError("Input string is not valid base64.")