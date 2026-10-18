"""Utility functions for image processing, embedding, and search"""

import numpy as np
from PIL import Image
import json
from config import Config
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

clip_model = None
clip_preprocess = None
device = "cpu"

try:
    import torch
    import clip
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Loading CLIP model on device: {device}")
    clip_model, clip_preprocess = clip.load(Config.CLIP_MODEL_NAME, device=device)
    logger.info("CLIP model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load CLIP model: {e}")
    logger.warning("Image embedding features will be limited")

# Check if pytesseract is available
TESSERACT_AVAILABLE = False
try:
    import pytesseract
    # Test if tesseract is actually installed
    pytesseract.get_tesseract_version()
    TESSERACT_AVAILABLE = True
    logger.info("Tesseract OCR is available")
except Exception as e:
    logger.warning(f"Tesseract OCR not available: {e}")
    logger.warning("OCR features will be disabled")

# Check sklearn
SKLEARN_AVAILABLE = False
try:
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except Exception as e:
    logger.warning(f"scikit-learn not available: {e}")

def allowed_file(filename):
    """Check if file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def compute_clip_embedding(image_path):
    """
    Compute CLIP embedding for an image

    Args:
        image_path: Path to the image file

    Returns:
        numpy array of the embedding vector
    """
    if clip_model is None or clip_preprocess is None:
        logger.error("CLIP model not loaded, cannot compute embedding")
        raise Exception("CLIP model not available. Please install: pip install git+https://github.com/openai/CLIP.git")

    try:
        import torch
        image = Image.open(image_path).convert('RGB')
        image_input = clip_preprocess(image).unsqueeze(0).to(device)

        with torch.no_grad():
            image_features = clip_model.encode_image(image_input)
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)

        embedding_array = image_features.cpu().numpy()[0]

        # 检查嵌入是否有效
        if embedding_array is None or len(embedding_array) == 0:
            logger.error(f"Computed embedding is None or empty for {image_path}")
            raise Exception("Failed to compute valid image embedding")

        return embedding_array
    except Exception as e:
        logger.error(f"Error computing embedding for {image_path}: {e}")
        raise Exception(f"Failed to compute image embedding: {str(e)}")

def compute_text_embedding(text):
    """
    Compute CLIP embedding for text

    Args:
        text: Text string to encode

    Returns:
        numpy array of the embedding vector
    """
    if clip_model is None:
        logger.error("CLIP model not loaded")
        return np.zeros(512)

    try:
        text_input = clip.tokenize([text]).to(device)

        with torch.no_grad():
            text_features = clip_model.encode_text(text_input)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)

        return text_features.cpu().numpy()[0]
    except Exception as e:
        logger.error(f"Error computing text embedding: {e}")
        return np.zeros(512)

def extract_ocr_text(image_path):
    """
    Extract text from image using OCR

    Args:
        image_path: Path to the image file

    Returns:
        Extracted text string
    """
    if not TESSERACT_AVAILABLE:
        logger.warning("Tesseract not available, returning empty string")
        return ""

    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting OCR text from {image_path}: {e}")
        return ""

def find_similar_images(image_id=None, embedding=None, limit=10):
    """
    Find similar images using cosine similarity on embeddings

    Args:
        image_id: ID of the image to find similar images for (optional)
        embedding: Numpy array embedding to search with (optional)
        limit: Maximum number of results to return

    Returns:
        List of tuples (Image object, similarity score)
    """
    if not SKLEARN_AVAILABLE:
        logger.error("scikit-learn not available for similarity search")
        return []

    # Import here to avoid circular dependency
    from app import app, db, Image

    try:
        with app.app_context():
            if image_id is not None:
                # Get the reference image
                ref_image = Image.query.get(image_id)
                if not ref_image or not ref_image.embedding:
                    return []
                query_embedding = np.array(json.loads(ref_image.embedding))
            elif embedding is not None:
                query_embedding = embedding
            else:
                return []

            # Get all images with embeddings
            all_images = Image.query.filter(Image.embedding.isnot(None)).all()

            if not all_images:
                return []

            # Compute similarities
            similarities = []
            for img in all_images:
                if image_id and img.id == image_id:
                    continue  # Skip the query image itself

                img_embedding = np.array(json.loads(img.embedding))
                similarity = cosine_similarity(
                    query_embedding.reshape(1, -1),
                    img_embedding.reshape(1, -1)
                )[0][0]
                similarities.append((img, float(similarity)))

            # Sort by similarity (descending) and return top-k
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:limit]

    except Exception as e:
        logger.error(f"Error finding similar images: {e}")
        return []

def search_by_text(query_text, limit=20):
    """
    Search images by text using CLIP text encoding

    Args:
        query_text: Text query string
        limit: Maximum number of results to return

    Returns:
        List of tuples (Image object, similarity score)
    """
    try:
        # Compute text embedding
        text_embedding = compute_text_embedding(query_text)

        # Find similar images
        return find_similar_images(embedding=text_embedding, limit=limit)

    except Exception as e:
        logger.error(f"Error in text search: {e}")
        return []

def search_by_ocr(query_text):
    """
    Search images by OCR text content (substring match)

    Args:
        query_text: Text to search for in OCR content

    Returns:
        List of Image objects
    """
    # Import here to avoid circular dependency
    from app import app, Image

    try:
        with app.app_context():
            # Case-insensitive substring search
            results = Image.query.filter(
                Image.ocr_text.ilike(f'%{query_text}%')
            ).all()

            return results

    except Exception as e:
        logger.error(f"Error in OCR search: {e}")
        return []

def auto_categorize_image(image_path):
    """
    Automatically categorize an image using CLIP

    Args:
        image_path: Path to the image file

    Returns:
        Category label string
    """
    categories = [
        'flowers', 'food', 'cars', 'dogs', 'road signs',
        'buildings', 'landscapes', 'birds', 'electronics', 'people',
        'cats', 'trees', 'sky', 'water', 'mountains',
        'beaches', 'sunsets', 'clouds', 'animals', 'insects',
        'fruits', 'vegetables', 'desserts', 'beverages', 'furniture',
        'clothing', 'shoes', 'bags', 'jewelry', 'tools',
        'sports', 'musical instruments', 'books', 'art', 'toys',
        'medical', 'school', 'office', 'kitchen', 'bathroom',
        'bedroom', 'living room', 'garden', 'park', 'city',
        'countryside', 'forest', 'rivers', 'lakes', 'oceans'
    ]

    if clip_model is None or clip_preprocess is None:
        logger.warning("CLIP model not available for auto-categorization")
        return 'uncategorized'

    try:
        image = Image.open(image_path).convert('RGB')
        image_input = clip_preprocess(image).unsqueeze(0).to(device)
        text_inputs = clip.tokenize([f"a photo of {cat}" for cat in categories]).to(device)

        with torch.no_grad():
            image_features = clip_model.encode_image(image_input)
            text_features = clip_model.encode_text(text_inputs)

            # Normalize features
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)

            # Calculate similarity
            similarity = (image_features @ text_features.T).softmax(dim=-1)

        # Get the category with highest similarity
        category_idx = similarity.argmax().item()
        confidence = similarity[0][category_idx].item()

        logger.info(f"Image categorized as '{categories[category_idx]}' with confidence {confidence:.4f}")

        return categories[category_idx]

    except Exception as e:
        logger.error(f"Error auto-categorizing image: {e}")
        return 'uncategorized'

def get_analytics_data():
    """
    Get analytics data for the dashboard

    Returns:
        Dictionary with analytics information
    """
    # Import here to avoid circular dependency
    from app import app, db, Image, User, SearchLog
    from sqlalchemy import func
    from collections import defaultdict

    try:
        with app.app_context():
            # Basic statistics
            total_images = Image.query.count()
            total_users = User.query.count()
            total_storage = db.session.query(func.sum(Image.file_size)).scalar() or 0
            total_downloads = db.session.query(func.sum(Image.download_count)).scalar() or 0

            # Category distribution
            category_stats = db.session.query(
                Image.category,
                func.count(Image.id)
            ).group_by(Image.category).all()

            category_distribution = {
                cat or 'Uncategorized': count
                for cat, count in category_stats
            }

            # Upload trends (by day for last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)

            recent_uploads = db.session.query(
                func.date(Image.upload_date).label('date'),
                func.count(Image.id).label('count')
            ).filter(
                Image.upload_date >= thirty_days_ago
            ).group_by(
                func.date(Image.upload_date)
            ).all()

            upload_trends = {
                str(date): count
                for date, count in recent_uploads
            }

            # File size distribution
            size_ranges = [
                ('< 100KB', 0, 100 * 1024),
                ('100KB - 500KB', 100 * 1024, 500 * 1024),
                ('500KB - 1MB', 500 * 1024, 1024 * 1024),
                ('1MB - 5MB', 1024 * 1024, 5 * 1024 * 1024),
                ('> 5MB', 5 * 1024 * 1024, float('inf'))
            ]

            size_distribution = {}
            for label, min_size, max_size in size_ranges:
                if max_size == float('inf'):
                    count = Image.query.filter(Image.file_size >= min_size).count()
                else:
                    count = Image.query.filter(
                        Image.file_size >= min_size,
                        Image.file_size < max_size
                    ).count()
                size_distribution[label] = count

            # Search statistics
            search_stats = db.session.query(
                SearchLog.search_type,
                func.count(SearchLog.id)
            ).group_by(SearchLog.search_type).all()

            search_type_distribution = {
                search_type: count
                for search_type, count in search_stats
            }

            # Most downloaded images
            top_downloads = Image.query.order_by(
                Image.download_count.desc()
            ).limit(10).all()

            # Get latency snapshots data
            latency_data = get_latency_snapshots()

            return {
                'total_images': total_images,
                'total_users': total_users,
                'total_storage': total_storage,
                'total_downloads': total_downloads,
                'category_distribution': category_distribution,
                'upload_trends': upload_trends,
                'size_distribution': size_distribution,
                'search_type_distribution': search_type_distribution,
                'top_downloads': [
                    {
                        'id': img.id,
                        'filename': img.original_filename,
                        'download_count': img.download_count
                    }
                    for img in top_downloads
                ],
                # Add latency snapshots data
                'latency_snapshots': latency_data.get('snapshots', []),
                'latency_breakdown': latency_data.get('breakdown', {}),
                'latency_trends': latency_data.get('trends', [])
            }

    except Exception as e:
        logger.error(f"Error getting analytics data: {e}")
        return {
            'total_images': 0,
            'total_users': 0,
            'total_storage': 0,
            'total_downloads': 0,
            'category_distribution': {},
            'upload_trends': {},
            'size_distribution': {},
            'search_type_distribution': {},
            'top_downloads': [],
            'latency_snapshots': [],
            'latency_breakdown': {},
            'latency_trends': []
        }

def get_latency_snapshots(hours=24):
    """
    Get latency snapshots data for performance monitoring
    """
    try:
        from app import app, db, PerformanceLog
        from sqlalchemy import func
        import numpy as np

        with app.app_context():
            # Calculate time range
            time_threshold = datetime.utcnow() - timedelta(hours=hours)

            logs = PerformanceLog.query.filter(
                PerformanceLog.timestamp >= time_threshold
            ).all()

            if not logs:
                return {
                    'snapshots': [],
                    'breakdown': {},
                    'trends': []
                }

            # Group logs by operation type
            logs_by_operation = {}
            for log in logs:
                if log.operation_type not in logs_by_operation:
                    logs_by_operation[log.operation_type] = []
                logs_by_operation[log.operation_type].append(log)

            # Calculate latency statistics for each operation type
            snapshots = []

            for op_type, op_logs in logs_by_operation.items():
                latencies = [log.latency for log in op_logs]

                if latencies:
                    # Basic statistics
                    avg_latency = np.mean(latencies)
                    p95_latency = np.percentile(latencies, 95)
                    max_latency = np.max(latencies)
                    min_latency = np.min(latencies)
                    std_latency = np.std(latencies)

                    snapshots.append({
                        'operation_type': op_type,
                        'avg_latency': float(avg_latency),
                        'p95_latency': float(p95_latency),
                        'max_latency': float(max_latency),
                        'min_latency': float(min_latency),
                        'std_latency': float(std_latency),
                        'request_count': len(op_logs)
                    })

            # Calculate trends (last 7 days)
            trends = get_latency_trends(days=7)

            return {
                'snapshots': snapshots,
                'breakdown': {},
                'trends': trends
            }

    except Exception as e:
        logger.error(f"Error getting latency snapshots: {e}")
        return {
            'snapshots': [],
            'breakdown': {},
            'trends': []
        }

def get_latency_trends(days=7):
    """
    Get latency trends over time

    Args:
        days: Number of days to analyze

    Returns:
        List of trend data
    """
    try:
        from app import app, db, PerformanceLog
        from sqlalchemy import func
        import numpy as np

        with app.app_context():
            trends = []
            time_threshold = datetime.utcnow() - timedelta(days=days)

            # Group by date and operation type
            daily_stats = db.session.query(
                func.date(PerformanceLog.timestamp).label('date'),
                PerformanceLog.operation_type,
                func.avg(PerformanceLog.latency).label('avg_latency'),
                func.count(PerformanceLog.id).label('request_count')
            ).filter(
                PerformanceLog.timestamp >= time_threshold,
                PerformanceLog.operation_type.in_(['text_search', 'image_upload', 'ocr_search', 'similarity_search'])
            ).group_by(
                func.date(PerformanceLog.timestamp),
                PerformanceLog.operation_type
            ).order_by(
                func.date(PerformanceLog.timestamp)
            ).all()

            previous_day_data = {}
            for date, op_type, avg_latency, count in daily_stats:
                current_avg = float(avg_latency)

                trend = 0.0
                prev_key = f"{date}_{op_type}"
                if prev_key in previous_day_data:
                    prev_avg = previous_day_data[prev_key]
                    if prev_avg > 0:
                        trend = (current_avg - prev_avg) / prev_avg

                previous_day_data[prev_key] = current_avg

                trends.append({
                    'date': str(date),
                    'operation_type': op_type,
                    'avg_latency': current_avg,
                    'request_count': count,
                    'trend': float(trend)
                })

            return trends

    except Exception as e:
        logger.error(f"Error getting latency trends: {e}")
        return []