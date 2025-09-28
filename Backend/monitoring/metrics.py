"""
Metrics collection for StudHelper Backend
"""

import time
import psutil
import logging
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Class, ChatSession, UsageRecord

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collect application and system metrics"""
    
    def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system-level metrics"""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None,
                "timestamp": time.time()
            }
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return {}
    
    def collect_app_metrics(self, db: Session) -> Dict[str, Any]:
        """Collect application-level metrics"""
        try:
            # Count active entities
            active_users = db.query(User).filter(User.is_active == True).count()
            total_classes = db.query(Class).filter(Class.is_active == True).count()
            active_sessions = db.query(ChatSession).filter(ChatSession.is_active == True).count()
            
            # Recent activity (last 24 hours)
            from datetime import datetime, timedelta
            yesterday = datetime.utcnow() - timedelta(days=1)
            
            recent_messages = db.query(ChatSession).filter(
                ChatSession.updated_at >= yesterday
            ).count()
            
            recent_usage = db.query(UsageRecord).filter(
                UsageRecord.timestamp >= yesterday
            ).count()
            
            return {
                "active_users": active_users,
                "total_classes": total_classes,
                "active_chat_sessions": active_sessions,
                "recent_messages_24h": recent_messages,
                "recent_usage_records_24h": recent_usage,
                "timestamp": time.time()
            }
        except Exception as e:
            logger.error(f"Error collecting app metrics: {e}")
            return {}
    
    def collect_all_metrics(self) -> Dict[str, Any]:
        """Collect all available metrics"""
        db = next(get_db())
        try:
            return {
                "system": self.collect_system_metrics(),
                "application": self.collect_app_metrics(db),
                "timestamp": time.time()
            }
        finally:
            db.close()

