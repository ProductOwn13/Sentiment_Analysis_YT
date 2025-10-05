# YouTube Transcript Analyzer - Setup and Usage Instructions

## Overview
This project analyzes YouTube video transcripts for sentiment analysis and provides a web interface to visualize the results.

## Project Structure
```
SentimentAnl/
├── app.py                    # Flask web application
├── YT_transcript.py          # YouTube transcript fetcher
├── sentiment_analyzer.py     # Sentiment analysis engine
├── templates/
│   └── index.html           # Web interface template
└── instructions.md          # This file
```

## Prerequisites
- Python 3.7 or higher
- Virtual environment (myvenv)
- Internet connection

## Installation

### 1. Activate Virtual Environment
```bash
# Navigate to your project directory
cd "C:\My D Drive\myvenv\Sourabh'sProg\SentimentAnl"

# Activate virtual environment
..\Scripts\activate
```

### 2. Install Required Packages
```bash
pip install youtube-transcript-api textblob nltk flask matplotlib
```

### 3. Download NLTK Data (First Time Only)
Run Python and execute:
```python
import nltk
nltk.download('punkt')
nltk.download('vader_lexicon')
```

## Running the Application

### Option 1: Web Interface (Recommended)
1. **Start the Flask server:**
   ```bash
   python app.py
   ```

2. **Open your web browser** and go to:
   ```
   http://127.0.0.1:5000
   ```

3. **Enter a YouTube URL** and click "Analyze Sentiment"

4. **View results** including:
   - Overall sentiment score
   - Visual charts
   - Statistical breakdown
   - Example sentences

### Option 2: Command Line Interface

#### Get YouTube Transcript Only:
```bash
python YT_transcript.py
```
- Enter YouTube URL when prompted
- Transcript will be printed to console

#### Analyze Sentiment from Saved Transcript:
```bash
python sentiment_analyzer.py
```
- Uses transcript from previous run
- Generates JSON results and charts

## Usage Examples

### Valid YouTube URL Formats:
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `VIDEO_ID` (just the ID)

### Example URLs to Test:
- `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- `https://youtu.be/dQw4w9WgXcQ`

## Output Files
The program generates several output files:

1. **Transcript Files**: `transcript_VIDEO_ID.txt`
2. **Sentiment Analysis**: `sentiment_analysis_VIDEO_ID.json`
3. **Visualization Charts**: `sentiment_charts_VIDEO_ID.png`

## Troubleshooting

### Common Issues:

#### 1. "No transcript available"
- Video may not have captions/subtitles
- Try a different video
- Check if URL is correct

#### 2. "Module not found" errors
```bash
# Ensure virtual environment is activated
..\Scripts\activate

# Reinstall packages
pip install --upgrade youtube-transcript-api textblob nltk flask matplotlib
```

#### 3. NLTK data missing
```python
import nltk
nltk.download('all')  # Downloads all NLTK data
```

#### 4. Port already in use
- Change port in `app.py`: `app.run(debug=True, port=5001)`
- Or kill existing process

### Git Configuration (if needed):
```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

## Features

### Sentiment Analysis Metrics:
- **Polarity**: -1 (negative) to 1 (positive)
- **Subjectivity**: 0 (objective) to 1 (subjective)
- **Sentence Classification**: Positive, Negative, Neutral

### Visualizations:
- Sentiment distribution pie chart
- Polarity progression line plot
- Subjectivity vs polarity scatter plot
- Statistical histograms

## API Endpoints (Web Interface)

- `GET /`: Main interface
- `POST /analyze`: Analyze YouTube URL
- Returns JSON with sentiment data and chart URLs

## Stopping the Application

### Web Interface:
- Press `Ctrl + C` in the terminal running Flask
- Close browser tab

### Deactivate Virtual Environment:
```bash
deactivate
```

## Support
If you encounter issues:
1. Check that all packages are installed
2. Verify YouTube URL is valid and has transcripts
3. Ensure virtual environment is activated
4. Check terminal output for error messages

## Example Workflow
1. Activate virtual environment
2. Run `python app.py`
3. Open browser to `http://127.0.0.1:5000`
4. Paste YouTube URL
5. Click "Analyze Sentiment"
6. View results and download charts
7. Press `Ctrl + C` to stop server