import os
from datetime import datetime

class Config:
    """Application configuration settings"""

    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-please-change-in-production'

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///image_drive.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    TEMP_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

    # Session configuration
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours

    # CLIP model configuration
    # ***
    CLIP_MODEL_NAME = 'ViT-L/14'
    IMAGENET_CLASSIFICATION = True
    CLASSIFICATION_BATCH_SIZE = 200
    ENABLE_CLASSIFICATION_CACHE = True
    CLASSIFICATION_CACHE_SIZE = 1000
    MIN_CLASSIFICATION_CONFIDENCE = 0.1

    # Search configuration
    SIMILARITY_TOP_K = 20

    # Pagination
    IMAGES_PER_PAGE = 20

    # Static file versioning (cache busting)
    STATIC_VERSION = str(int(datetime.now().timestamp()))

    # Disable caching in development
    SEND_FILE_MAX_AGE_DEFAULT = 0

    # ===== ONLINE SEARCH CONFIGURATION =====
    # Enable/disable online search features
    ENABLE_ONLINE_SEARCH = True

    # Unsplash API (Free tier: 50 requests/hour)
    # Get your API key at: https://unsplash.com/developers
    UNSPLASH_ACCESS_KEY = os.environ.get('UNSPLASH_ACCESS_KEY') or ''

    # Pexels API (Free tier: 200 requests/hour)
    # Get your API key at: https://www.pexels.com/api/
    PEXELS_API_KEY = os.environ.get('PEXELS_API_KEY') or ''

    # Pixabay API (Free tier: 100 requests/minute)
    # Get your API key at: https://pixabay.com/api/docs/
    PIXABAY_API_KEY = os.environ.get('PIXABAY_API_KEY') or ''

    # Default online search provider: 'unsplash', 'pexels', 'pixabay', 'all'
    DEFAULT_ONLINE_PROVIDER = 'unsplash'

    # Number of results from online search
    ONLINE_SEARCH_LIMIT = 20
