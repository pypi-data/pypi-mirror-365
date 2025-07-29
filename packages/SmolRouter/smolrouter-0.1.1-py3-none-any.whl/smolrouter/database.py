import os
import logging
import re
import json
from datetime import datetime, timedelta
from peewee import *

logger = logging.getLogger("model-rerouter")

# Database configuration
DB_PATH = os.getenv("DB_PATH", "requests.db")
MAX_AGE_DAYS = int(os.getenv("MAX_LOG_AGE_DAYS", "7"))

# Initialize database
db = SqliteDatabase(DB_PATH)

def estimate_token_count(text: str) -> int:
    """Estimate token count for text content.
    
    Uses a simple but reasonably accurate heuristic:
    - Split on whitespace and punctuation
    - Count tokens roughly as words + punctuation marks
    - Better than simple character/4 for real-world text
    
    Args:
        text: Input text to count tokens for
        
    Returns:
        Estimated token count
    """
    if not text or not isinstance(text, str):
        return 0
    
    # Split on whitespace and common punctuation
    # This gives a decent approximation for most text
    tokens = re.findall(r'\b\w+\b|[^\w\s]', text.lower())
    return len(tokens)

def extract_tokens_from_openai_response(response_data: dict) -> tuple[int, int, int]:
    """Extract token counts from OpenAI response usage data.
    
    Args:
        response_data: OpenAI API response dictionary
        
    Returns:
        Tuple of (prompt_tokens, completion_tokens, total_tokens)
        Returns (0, 0, 0) if usage data not available
    """
    usage = response_data.get('usage', {})
    if not usage:
        return (0, 0, 0)
    
    prompt_tokens = usage.get('prompt_tokens', 0)
    completion_tokens = usage.get('completion_tokens', 0) 
    total_tokens = usage.get('total_tokens', 0)
    
    return (prompt_tokens, completion_tokens, total_tokens)

def estimate_tokens_from_request(request_data: dict) -> int:
    """Estimate token count from request payload.
    
    Args:
        request_data: Request payload dictionary
        
    Returns:
        Estimated prompt token count
    """
    if not request_data:
        return 0
        
    total_text = ""
    
    # Handle OpenAI format
    if 'messages' in request_data:
        for message in request_data.get('messages', []):
            if isinstance(message, dict) and 'content' in message:
                total_text += str(message['content']) + " "
    
    # Handle legacy prompt format
    if 'prompt' in request_data:
        total_text += str(request_data['prompt']) + " "
    
    return estimate_token_count(total_text)

class BaseModel(Model):
    class Meta:
        database = db

class RequestLog(BaseModel):
    """Log of all requests and responses through the proxy"""
    id = AutoField()
    timestamp = DateTimeField(default=datetime.now)
    
    # Request details
    source_ip = CharField(max_length=45)  # IPv6 compatible
    method = CharField(max_length=10)
    path = CharField(max_length=500)
    service_type = CharField(max_length=10)  # 'openai' or 'ollama'
    
    # Upstream details
    upstream_url = CharField(max_length=500)
    
    # Model mapping
    original_model = CharField(max_length=200, null=True)
    mapped_model = CharField(max_length=200, null=True)
    
    # Performance metrics
    duration_ms = IntegerField(null=True)
    request_size = IntegerField(default=0)
    response_size = IntegerField(default=0)
    status_code = IntegerField(null=True)
    
    # Token metrics for performance analytics
    prompt_tokens = IntegerField(null=True)
    completion_tokens = IntegerField(null=True) 
    total_tokens = IntegerField(null=True)
    
    # Request status tracking
    completed_at = DateTimeField(null=True)  # NULL = inflight, NOT NULL = completed
    
    # Payload storage (large blobs)
    request_body = BlobField(null=True)
    response_body = BlobField(null=True)
    
    # Error tracking
    error_message = TextField(null=True)
    
    class Meta:
        indexes = (
            # Index for common queries
            (('timestamp',), False),
            (('service_type', 'timestamp'), False),
            (('status_code', 'timestamp'), False),
            (('completed_at',), False),  # For inflight queries
            (('prompt_tokens', 'duration_ms'), False),  # For performance analytics
        )

def init_database():
    """Initialize database and create tables"""
    try:
        if not db.is_connection_usable():
            db.connect()
        db.create_tables([RequestLog], safe=True)
        logger.info(f"Database initialized at {DB_PATH}")
        
        # Run cleanup on startup
        cleanup_old_logs()
        vacuum_database()
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

def cleanup_old_logs():
    """Remove logs older than MAX_AGE_DAYS"""
    try:
        cutoff_date = datetime.now() - timedelta(days=MAX_AGE_DAYS)
        deleted_count = RequestLog.delete().where(RequestLog.timestamp < cutoff_date).execute()
        
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old log entries (older than {MAX_AGE_DAYS} days)")
        
    except Exception as e:
        logger.error(f"Failed to cleanup old logs: {e}")

def vacuum_database():
    """Run VACUUM to reclaim space after cleanup"""
    try:
        db.execute_sql("VACUUM")
        logger.info("Database vacuum completed")
    except Exception as e:
        logger.error(f"Failed to vacuum database: {e}")

def get_recent_logs(limit=100, service_type=None):
    """Get recent request logs"""
    query = RequestLog.select().order_by(RequestLog.timestamp.desc()).limit(limit)
    
    if service_type:
        query = query.where(RequestLog.service_type == service_type)
    
    return list(query)

def get_inflight_requests():
    """Get currently inflight (incomplete) requests"""
    try:
        return list(RequestLog.select().where(RequestLog.completed_at.is_null()).order_by(RequestLog.timestamp.desc()))
    except Exception as e:
        logger.error(f"Failed to get inflight requests: {e}")
        return []

def get_log_stats():
    """Get basic statistics about the logs"""
    try:
        total_requests = RequestLog.select().count()
        
        # Count by service type
        openai_count = RequestLog.select().where(RequestLog.service_type == 'openai').count()
        ollama_count = RequestLog.select().where(RequestLog.service_type == 'ollama').count()
        
        # Recent activity (last 24 hours)
        yesterday = datetime.now() - timedelta(days=1)
        recent_count = RequestLog.select().where(RequestLog.timestamp > yesterday).count()
        
        # Inflight requests
        inflight_count = RequestLog.select().where(RequestLog.completed_at.is_null()).count()
        
        return {
            'total_requests': total_requests,
            'openai_requests': openai_count,
            'ollama_requests': ollama_count,
            'recent_requests': recent_count,
            'inflight_requests': inflight_count
        }
    except Exception as e:
        logger.error(f"Failed to get log stats: {e}")
        return {
            'total_requests': 0,
            'openai_requests': 0,
            'ollama_requests': 0,
            'recent_requests': 0,
            'inflight_requests': 0
        }