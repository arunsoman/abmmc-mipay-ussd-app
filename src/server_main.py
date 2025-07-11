import os
import json
import logging
from fastapi import FastAPI, Request
from fastapi.responses import Response
from src.ussd_handler import USSDGatewayHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set current working directory to project root
os.chdir(os.path.dirname(os.path.abspath(__file__)))
logger.info(f"Current working directory: {os.getcwd()}")

# Initialize FastAPI app
app = FastAPI(title="USSD Gateway", description="High-performance USSD server")

# Load configuration
try:
    config_path = os.path.join(os.getcwd(), '..' , "config", "demo_menu_config.json")
    if not os.path.exists(config_path):
        logger.error(f"Config file not found: {os.path.abspath(config_path)}")
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path, 'r') as f:
        config = json.load(f)
    config_mapping = {"*220#": config, "*220#1": config}
except Exception as e:
    logger.error(f"Failed to load config: {e}")
    raise

# Initialize USSD handler
handler = USSDGatewayHandler(config_mapping)

@app.post("/ussd")
async def handle_ussd(request: Request):
    """Handle USSD POST requests with minimal latency"""
    try:
        # Read raw XML body asynchronously
        xml_data = await request.body()
        xml_str = xml_data.decode('utf-8')
        
        # Process request using existing handler
        response_xml = handler.handle_request(xml_str)
        
        # Return XML response
        return Response(content=response_xml, media_type="application/xml")
    except Exception as e:
        logger.error(f"Request handling failed: {e}")
        return Response(
            content=f'<?xml version="1.0" encoding="UTF-8"?><dialog type="End" error="true"><error>{str(e)}</error></dialog>',
            media_type="application/xml",
            status_code=500
        )

if __name__ == "__main__":
    import uvicorn
    # Run Uvicorn with optimized settings
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=3214,
        workers=1,  # Single worker for simplicity; adjust for production
        log_level="error",  # Minimize logging overhead
        access_log=False,   # Disable access logging for performance
        timeout_keep_alive=5  # Optimize for short-lived USSD connections
    )