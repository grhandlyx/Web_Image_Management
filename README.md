# Image Drive - Intelligent Web Image Management System

A Flask-based web application for intelligent image management with semantic search, OCR, and similarity retrieval.

## Project Overview

This project implements a production-ready Flask web application that functions as an intelligent image drive system for STAT7008 Course Project - Topic 3.

### Key Features

- **User Authentication**: Secure registration/login with password hashing and token-based sessions
- **Image Upload/Browse/Download**: Drag-and-drop upload, gallery view, and secure downloading
- **Semantic Search**: CLIP-based text-to-image search using natural language queries
- **OCR Search**: Full-text search over text extracted from images using Tesseract
- **Image Similarity**: Upload an image to find similar images in the database
- **Similar Images Panel**: View related images when viewing any image detail
- **Analytics Dashboard**: Category distribution, upload trends, size statistics
- **Logging System**: Structured logging with rotation for uploads, downloads, searches, and errors

## System Requirements

- Python 3.8 or higher
- Tesseract OCR installed on your system
- 4GB+ RAM recommended (for CLIP model)
- 500MB+ disk space

## Installation

### 1. Install System Dependencies

#### macOS:
```bash
brew install tesseract
```

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

#### Windows:
Download and install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Initialize Database

```bash
python init_database.py
```

This will:
- Create database tables
- Set up necessary directories
- Create a default admin user (username: `admin`, password: `admin123`)

## Running the Application

```bash
python app.py
```

The application will be available at: http://localhost:5000

## Usage Guide

### 1. Login/Register

- Access the application at http://localhost:5000
- Register a new account or login with the default admin account
- Default credentials: `admin` / `admin123` (please change after first login)

### 2. Upload Images

#### Single Image Upload
- Click "Upload Images" button in the gallery
- Select one or multiple images
- Images will be automatically processed:
  - Embedded using CLIP
  - OCR processed for text extraction
  - Auto-categorized into one of 10 categories

#### Batch Upload
- Open `search_analysis.ipynb` in the root directory
- Run the first three cells of the notebook
- This will process all images in batch mode with the same automated processing:
  - CLIP embeddings
  - OCR text extraction
  - Auto-categorization into 10 categories

### 3. Search Functions

**Semantic Text Search:**
- Enter natural language descriptions (e.g., "red flowers", "modern buildings")
- System encodes query and finds semantically similar images

**OCR Search:**
- Search for text contained within images
- Supports substring matching

**Similar Image Search:**
- Upload a reference image
- System finds visually similar images using CLIP embeddings

### 4. Image Details

- Click any image to view details
- See metadata, OCR text, and similar images panel
- Download images directly

### 5. Analytics

- View analytics dashboard for:
  - Total images, users, storage, downloads
  - Latency Snapshots (Last 24 Hours)
  - Category distribution
  - Upload trends
  - File size distribution
  - Search statistics
- Export data as CSV or JSON

## Project Structure

```
project/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── utils.py               # CLIP, OCR, and search utilities
├── init_database.py       # Database initialization script
├── tradeoff.py            # Analysis of index size vs memory tradeoff
├── requirements.txt       # Python dependencies
├── templates/             # HTML templates
│   ├── base.html          # Base template
│   ├── login.html         # Login page
│   ├── register.html      # Registration page
│   ├── gallery.html       # Image gallery
│   ├── detail.html        # Image detail view
│   ├── analytics.html     # Analytics dashboard
│   └── error.html         # Error page
├── static/                # Static files
│   ├── css/
│   │   └── style.css      # Main stylesheet
│   └── js/
│       └── main.js        # JavaScript utilities
├── uploads/               # Image storage (created automatically)
├── temp/                  # Temporary files (created automatically)
├── CLIP_image/            # images for CLIP pending uploaded
├── OCR/                   # images for OCR pending uploaded
└── logs/                  # Application logs (created automatically)
```

## Database Schema

### User Table
- `id`: Primary key
- `username`: Unique username
- `email`: Unique email
- `password_hash`: Hashed password
- `created_at`: Account creation timestamp

### Session Table
- `id`: Primary key
- `user_id`: Foreign key to User
- `token`: Unique session token
- `expires_at`: Session expiration time
- `created_at`: Session creation timestamp

### Image Table
- `id`: Primary key
- `filename`: Stored filename
- `original_filename`: Original upload name
- `file_path`: Full file path
- `file_hash`: SHA-256 hash for deduplication
- `file_size`: File size in bytes
- `category`: Auto-detected category
- `ocr_text`: Extracted text from OCR
- `embedding`: CLIP embedding (JSON)
- `user_id`: Foreign key to User
- `upload_date`: Upload timestamp
- `download_count`: Download counter

### SearchLog Table
- `id`: Primary key
- `user_id`: Foreign key to User
- `search_type`: Type of search (text/ocr/similarity)
- `query`: Search query
- `results_count`: Number of results
- `timestamp`: Search timestamp

## API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User login
- `GET /logout` - User logout

### Image Management
- `POST /upload` - Upload image
- `GET /gallery` - View gallery (paginated)
- `GET /image/<id>` - Image detail view
- `GET /download/<id>` - Download image
- `GET /serve/<id>` - Serve image file

### Search
- `GET /search/text?q=<query>` - Semantic text search
- `GET /search/ocr?q=<query>` - OCR text search
- `POST /search/similar` - Image similarity search

### Analytics
- `GET /analytics` - Analytics dashboard
- `GET /analytics/export?format=<csv|json>` - Export analytics data

## Features Implementation

### 1. Embedding Pipeline
- Images are embedded once at upload using CLIP ViT-B/32
- Embeddings stored as JSON in database
- No re-embedding on search (efficient retrieval)

### 2. Auto-Categorization
- Categories: 'flowers', 'food', 'cars', 'dogs', 'road signs',
        'buildings', 'landscapes', 'birds', 'electronics', 'people',
        'cats', 'trees', 'sky', 'water', 'mountains',
        'beaches', 'sunsets', 'clouds', 'animals', 'insects',
        'fruits', 'vegetables', 'desserts', 'beverages', 'furniture',
        'clothing', 'shoes', 'bags', 'jewelry', 'tools',
        'sports', 'musical instruments', 'books', 'art', 'toys',
        'medical', 'school', 'office', 'kitchen', 'bathroom',
        'bedroom', 'living room', 'garden', 'park', 'city',
        'countryside', 'forest', 'rivers', 'lakes', 'oceans'
- CLIP zero-shot classification at upload time

### 3. Deduplication
- SHA-256 hash computed for each upload
- Duplicate detection prevents redundant storage

### 4. Session Management
- Token-based sessions with 24-hour expiry
- Secure session handling with refresh capability

### 5. Logging System
- Rotating file handler (10MB per file, 10 backups)
- Structured logs for all operations
- Located in `logs/app.log`

## Security Features

- Password hashing with Werkzeug
- Token-based session management
- File type validation
- Secure filename handling
- SQL injection protection via SQLAlchemy ORM

## Performance Considerations

- Lazy image loading in gallery
- Pagination for large image collections
- Vector similarity computed in-memory (suitable for small-medium datasets)
- For large-scale deployment, consider:
  - Vector database (FAISS, pgvector)
  - Redis for session storage
  - CDN for image serving
  - Background task queue for embedding computation

## Troubleshooting

### Tesseract not found
```bash
# Make sure Tesseract is installed and in PATH
tesseract --version
```

### CLIP model download issues
- First run will download CLIP model (~350MB)
- Ensure stable internet connection

### Database locked errors
- Stop all running instances
- Delete `image_drive.db` and reinitialize

### Out of memory
- CLIP model requires ~2GB RAM
- Consider using CPU mode if GPU memory insufficient

### No Online Search Access
If you cannot perform online searches, follow these steps to configure Unsplash API access:

1. Visit [Unsplash Developers](https://unsplash.com/developers)
2. Click "Register as a developer"
3. Click "New Application"
4. Get your Access Key and paste it into `config.py`:

```bash
UNSPLASH_ACCESS_KEY = os.environ.get('UNSPLASH_ACCESS_KEY') or 'your_access_key_here'
```

## License

This project is created for STAT7008 Course Project.

## Author

STAT7008 Student - 2025
