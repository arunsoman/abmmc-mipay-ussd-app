import os
import json
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, Request, HTTPException
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
    config_path = os.path.join(os.getcwd(), '..', "config", "demo_menu_config.json")
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

# Thread pool configuration
MAX_WORKERS = 5  # Maximum number of concurrent users
thread_pool = ThreadPoolExecutor(max_workers=MAX_WORKERS)

# Request queue and active connections tracking
request_queue = asyncio.Queue()
active_connections = 0
max_connections = MAX_WORKERS

def process_ussd_request(xml_str: str) -> str:
    """Process USSD request in thread pool"""
    try:
        return handler.handle_request(xml_str)
    except Exception as e:
        logger.error(f"Thread processing failed: {e}")
        return f'<?xml version="1.0" encoding="UTF-8"?><dialog type="End" error="true"><error>{str(e)}</error></dialog>'

@app.post("/ussd")
async def handle_ussd(request: Request):
    """Handle USSD POST requests with connection limiting and thread pool"""
    global active_connections
    
    # Check connection limit
    if active_connections >= max_connections:
        logger.warning(f"Connection limit reached: {active_connections}/{max_connections}")
        raise HTTPException(
            status_code=503, 
            detail="Service temporarily unavailable - too many concurrent connections"
        )
    
    try:
        # Increment active connections
        active_connections += 1
        logger.info(f"Active connections: {active_connections}/{max_connections}")
        
        # Read raw XML body asynchronously
        xml_data = await request.body()
        xml_str = xml_data.decode('utf-8')
        
        # Submit to thread pool and await result
        loop = asyncio.get_event_loop()
        response_xml = await loop.run_in_executor(
            thread_pool, 
            process_ussd_request, 
            xml_str
        )
        
        # Return XML response
        return Response(content=response_xml, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Request handling failed: {e}")
        return Response(
            content=f'<?xml version="1.0" encoding="UTF-8"?><dialog type="End" error="true"><error>{str(e)}</error></dialog>',
            media_type="application/xml",
            status_code=500
        )
    finally:
        # Decrement active connections
        active_connections -= 1
        logger.info(f"Connection completed. Active connections: {active_connections}/{max_connections}")

@app.get("/health")
async def health_check():
    """Health check endpoint with connection status"""
    return {
        "status": "healthy",
        "active_connections": active_connections,
        "max_connections": max_connections,
        "available_slots": max_connections - active_connections
    }

@app.get("/stats")
async def get_stats():
    """Get server statistics"""
    return {
        "thread_pool_size": MAX_WORKERS,
        "active_connections": active_connections,
        "max_connections": max_connections,
        "queue_size": request_queue.qsize() if hasattr(request_queue, 'qsize') else 0
    }

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting USSD Gateway with {MAX_WORKERS} worker threads")
    logger.info(f"Maximum concurrent connections: {max_connections}")
    
    # Run Uvicorn with optimized settings
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=3214,
        workers=1,  # Single worker for thread pool management
        log_level="error",
        access_log=False,
        timeout_keep_alive=5
    )