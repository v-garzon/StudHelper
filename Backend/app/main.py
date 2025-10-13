from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.firebase_admin import initialize_firebase
from app.config import get_settings
from app.database import create_tables
from app.routes import auth, classes, documents
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title="StudHelper API",
    description="Class-based AI learning platform API",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
create_tables()

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(classes.router, prefix="/api/v1/classes", tags=["Classes"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting StudHelper API...")
    
    # Initialize Firebase Admin SDK
    try:
        initialize_firebase()
        logger.info("Firebase initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        # Don't crash the app, but log the error
    
    logger.info("StudHelper API started successfully")

@app.get("/")
async def root():
    return {"message": "StudHelper API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# ============================================================================
# FRONTEND FILES
# ============================================================================


