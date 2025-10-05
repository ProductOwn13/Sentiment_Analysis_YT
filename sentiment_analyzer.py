# Sentiment Analysis for YouTube Transcripts
# This script loads transcript from the existing script and performs sentiment analysis

import sys
import os
from textblob import TextBlob
from collections import Counter
import json
from datetime import datetime

# Optional matplotlib import
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Matplotlib not available. Visualization will be skipped.")

# Add the SentimentAnl directory to path to import the transcript loader
sys.path.append(r'c:\My D Drive\myvenv\Sourabh\'sProg\SentimentAnl')

# Import the transcript loading function
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    import re
except ImportError:
    print("Required libraries not found. Please install youtube-transcript-api and textblob")
    sys.exit(1)

def get_video_id(url):
    """Extract video ID from YouTube URL."""
    match = re.search(r'(?:v=|youtu.be/)([\w-]+)', url)
    return match.group(1) if match else url

def load_transcript_text(video_url_or_id):
    """Load transcript and return as concatenated text."""
    video_id = get_video_id(video_url_or_id)
    try:
        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id, languages=['en'])
        return " ".join([entry.text for entry in transcript])
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return ""

def analyze_sentiment(text):
    """Perform comprehensive sentiment analysis."""
    if not text:
        return None
    
    # Create TextBlob object
    blob = TextBlob(text)
    
    # Overall sentiment
    overall_sentiment = blob.sentiment
    
    # Sentence-by-sentence analysis
    sentences = blob.sentences
    sentence_sentiments = []
    
    for sentence in sentences:
        sent = sentence.sentiment
        sentence_sentiments.append({
            'text': str(sentence),
            'polarity': sent.polarity,
            'subjectivity': sent.subjectivity
        })
    
    # Calculate statistics
    polarities = [s['polarity'] for s in sentence_sentiments]
    subjectivities = [s['subjectivity'] for s in sentence_sentiments]
    
    # Categorize sentiments
    positive_count = len([p for p in polarities if p > 0.1])
    negative_count = len([p for p in polarities if p < -0.1])
    neutral_count = len([p for p in polarities if -0.1 <= p <= 0.1])
    
    analysis_result = {
        'overall_polarity': overall_sentiment.polarity,
        'overall_subjectivity': overall_sentiment.subjectivity,
        'total_sentences': len(sentences),
        'positive_sentences': positive_count,
        'negative_sentences': negative_count,
        'neutral_sentences': neutral_count,
        'average_polarity': sum(polarities) / len(polarities) if polarities else 0,
        'average_subjectivity': sum(subjectivities) / len(subjectivities) if subjectivities else 0,
        'sentence_details': sentence_sentiments
    }
    
    return analysis_result

def interpret_sentiment(polarity, subjectivity):
    """Provide human-readable interpretation of sentiment scores."""
    # Polarity interpretation
    if polarity > 0.5:
        polarity_desc = "Very Positive"
    elif polarity > 0.1:
        polarity_desc = "Positive"
    elif polarity > -0.1:
        polarity_desc = "Neutral"
    elif polarity > -0.5:
        polarity_desc = "Negative"
    else:
        polarity_desc = "Very Negative"
    
    # Subjectivity interpretation
    if subjectivity > 0.7:
        subjectivity_desc = "Very Subjective (Opinion-based)"
    elif subjectivity > 0.3:
        subjectivity_desc = "Moderately Subjective"
    else:
        subjectivity_desc = "Objective (Fact-based)"
    
    return polarity_desc, subjectivity_desc

def create_sentiment_visualization(analysis_result, video_id):
    """Create visualization of sentiment analysis."""
    if not MATPLOTLIB_AVAILABLE:
        print("Matplotlib not available. Skipping visualization.")
        return
    
    try:
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
        
        # Pie chart of sentiment categories
        labels = ['Positive', 'Negative', 'Neutral']
        sizes = [analysis_result['positive_sentences'], 
                analysis_result['negative_sentences'], 
                analysis_result['neutral_sentences']]
        colors = ['lightgreen', 'lightcoral', 'lightblue']
        
        ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax1.set_title('Sentiment Distribution')
        
        # Polarity over time (sentence index)
        sentence_indices = range(len(analysis_result['sentence_details']))
        polarities = [s['polarity'] for s in analysis_result['sentence_details']]
        
        ax2.plot(sentence_indices, polarities, marker='o', markersize=2)
        ax2.axhline(y=0, color='r', linestyle='--', alpha=0.5)
        ax2.set_title('Sentiment Polarity Over Time')
        ax2.set_xlabel('Sentence Index')
        ax2.set_ylabel('Polarity (-1 to 1)')
        
        # Histogram of polarity distribution
        ax3.hist(polarities, bins=20, alpha=0.7, color='skyblue')
        ax3.set_title('Polarity Distribution')
        ax3.set_xlabel('Polarity Score')
        ax3.set_ylabel('Frequency')
        
        # Subjectivity vs Polarity scatter
        subjectivities = [s['subjectivity'] for s in analysis_result['sentence_details']]
        ax4.scatter(subjectivities, polarities, alpha=0.6)
        ax4.set_title('Subjectivity vs Polarity')
        ax4.set_xlabel('Subjectivity (0 to 1)')
        ax4.set_ylabel('Polarity (-1 to 1)')
        
        plt.tight_layout()
        plt.savefig(f'sentiment_analysis_{video_id}.png', dpi=300, bbox_inches='tight')
        plt.show()
        
    except Exception as e:
        print(f"Error creating visualization: {e}")

def save_results(analysis_result, video_id, video_url):
    """Save analysis results to JSON file."""
    output = {
        'video_id': video_id,
        'video_url': video_url,
        'analysis_timestamp': str(datetime.now()),
        'sentiment_analysis': analysis_result
    }
    
    filename = f'sentiment_analysis_{video_id}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"Results saved to {filename}")

def main():
    """Main function to run sentiment analysis."""
    # Default video URL (you can change this)
    video_url = "https://www.youtube.com/watch?v=pidnIHdA1Y8"
    
    print(f"Loading transcript for: {video_url}")
    transcript_text = load_transcript_text(video_url)
    
    if not transcript_text:
        print("Failed to load transcript. Exiting.")
        return
    
    print(f"Transcript loaded. Length: {len(transcript_text)} characters")
    print("Performing sentiment analysis...")
    
    # Perform sentiment analysis
    analysis_result = analyze_sentiment(transcript_text)
    
    if not analysis_result:
        print("Failed to analyze sentiment. Exiting.")
        return
    
    # Display results
    print("\n" + "="*60)
    print("SENTIMENT ANALYSIS RESULTS")
    print("="*60)
    
    polarity_desc, subjectivity_desc = interpret_sentiment(
        analysis_result['overall_polarity'], 
        analysis_result['overall_subjectivity']
    )
    
    print(f"Overall Sentiment: {polarity_desc}")
    print(f"Polarity Score: {analysis_result['overall_polarity']:.3f} (-1 to 1)")
    print(f"Subjectivity: {subjectivity_desc}")
    print(f"Subjectivity Score: {analysis_result['overall_subjectivity']:.3f} (0 to 1)")
    print()
    print(f"Total Sentences Analyzed: {analysis_result['total_sentences']}")
    print(f"Positive Sentences: {analysis_result['positive_sentences']} ({analysis_result['positive_sentences']/analysis_result['total_sentences']*100:.1f}%)")
    print(f"Negative Sentences: {analysis_result['negative_sentences']} ({analysis_result['negative_sentences']/analysis_result['total_sentences']*100:.1f}%)")
    print(f"Neutral Sentences: {analysis_result['neutral_sentences']} ({analysis_result['neutral_sentences']/analysis_result['total_sentences']*100:.1f}%)")
    print()
    print(f"Average Polarity: {analysis_result['average_polarity']:.3f}")
    print(f"Average Subjectivity: {analysis_result['average_subjectivity']:.3f}")
    
    # Show most positive and negative sentences
    sentence_details = analysis_result['sentence_details']
    if sentence_details:
        most_positive = max(sentence_details, key=lambda x: x['polarity'])
        most_negative = min(sentence_details, key=lambda x: x['polarity'])
        
        print("\n" + "-"*40)
        print("MOST POSITIVE SENTENCE:")
        print(f"Score: {most_positive['polarity']:.3f}")
        print(f"Text: {most_positive['text'][:200]}...")
        
        print("\n" + "-"*40)
        print("MOST NEGATIVE SENTENCE:")
        print(f"Score: {most_negative['polarity']:.3f}")
        print(f"Text: {most_negative['text'][:200]}...")
    
    # Save results
    video_id = get_video_id(video_url)
    save_results(analysis_result, video_id, video_url)
    
    # Create visualization
    if MATPLOTLIB_AVAILABLE:
        try:
            create_sentiment_visualization(analysis_result, video_id)
        except Exception as e:
            print(f"\nError creating visualization: {e}")
    else:
        print("\nVisualization skipped (matplotlib not available).")

if __name__ == "__main__":
    main()