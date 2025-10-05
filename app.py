from flask import Flask, render_template, request, jsonify, send_file
import os
import sys
import json
import base64
from io import BytesIO
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from datetime import datetime
import re

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our modules
from YT_transcript import get_video_id, load_transcript_text
from sentiment_analyzer import analyze_sentiment, interpret_sentiment, create_sentiment_visualization

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'static'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        video_url = data.get('url', '').strip()
        
        if not video_url:
            return jsonify({'error': 'Please provide a YouTube URL'}), 400
        
        # Validate YouTube URL
        video_id = get_video_id(video_url)
        if not video_id or video_id == video_url:
            return jsonify({'error': 'Invalid YouTube URL'}), 400
        
        # Load transcript
        transcript_text = load_transcript_text(video_url)
        if not transcript_text:
            return jsonify({'error': 'Could not fetch transcript for this video. Make sure it has English captions.'}), 400
        
        # Perform sentiment analysis
        analysis_result = analyze_sentiment(transcript_text)
        if not analysis_result:
            return jsonify({'error': 'Failed to analyze sentiment'}), 500
        
        # Generate interpretation
        polarity_desc, subjectivity_desc = interpret_sentiment(
            analysis_result['overall_polarity'], 
            analysis_result['overall_subjectivity']
        )
        
        # Create visualizations
        chart_urls = create_charts(analysis_result, video_id)
        
        # Prepare response
        response_data = {
            'video_id': video_id,
            'video_url': video_url,
            'transcript_length': len(transcript_text),
            'analysis': {
                'overall_sentiment': polarity_desc,
                'polarity_score': round(analysis_result['overall_polarity'], 3),
                'subjectivity': subjectivity_desc,
                'subjectivity_score': round(analysis_result['overall_subjectivity'], 3),
                'total_sentences': analysis_result['total_sentences'],
                'positive_sentences': analysis_result['positive_sentences'],
                'negative_sentences': analysis_result['negative_sentences'],
                'neutral_sentences': analysis_result['neutral_sentences'],
                'positive_percentage': round(analysis_result['positive_sentences']/analysis_result['total_sentences']*100, 1),
                'negative_percentage': round(analysis_result['negative_sentences']/analysis_result['total_sentences']*100, 1),
                'neutral_percentage': round(analysis_result['neutral_sentences']/analysis_result['total_sentences']*100, 1),
                'average_polarity': round(analysis_result['average_polarity'], 3),
                'average_subjectivity': round(analysis_result['average_subjectivity'], 3)
            },
            'charts': chart_urls,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Get most positive and negative sentences
        if analysis_result['sentence_details']:
            most_positive = max(analysis_result['sentence_details'], key=lambda x: x['polarity'])
            most_negative = min(analysis_result['sentence_details'], key=lambda x: x['polarity'])
            
            response_data['analysis']['most_positive'] = {
                'score': round(most_positive['polarity'], 3),
                'text': most_positive['text'][:200] + ('...' if len(most_positive['text']) > 200 else '')
            }
            response_data['analysis']['most_negative'] = {
                'score': round(most_negative['polarity'], 3),
                'text': most_negative['text'][:200] + ('...' if len(most_negative['text']) > 200 else '')
            }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

def create_charts(analysis_result, video_id):
    """Create visualization charts and return their URLs."""
    chart_urls = {}
    
    try:
        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f'Sentiment Analysis for Video: {video_id}', fontsize=16)
        
        # 1. Pie chart of sentiment categories
        labels = ['Positive', 'Negative', 'Neutral']
        sizes = [analysis_result['positive_sentences'], 
                analysis_result['negative_sentences'], 
                analysis_result['neutral_sentences']]
        colors = ['#28a745', '#dc3545', '#6c757d']
        
        ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax1.set_title('Sentiment Distribution', fontsize=14, fontweight='bold')
        
        # 2. Polarity over time (sentence index)
        sentence_indices = range(len(analysis_result['sentence_details']))
        polarities = [s['polarity'] for s in analysis_result['sentence_details']]
        
        ax2.plot(sentence_indices, polarities, marker='o', markersize=1, linewidth=0.5, color='#007bff')
        ax2.axhline(y=0, color='red', linestyle='--', alpha=0.7)
        ax2.set_title('Sentiment Polarity Over Time', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Sentence Index')
        ax2.set_ylabel('Polarity (-1 to 1)')
        ax2.grid(True, alpha=0.3)
        
        # 3. Histogram of polarity distribution
        ax3.hist(polarities, bins=30, alpha=0.7, color='#17a2b8', edgecolor='black')
        ax3.set_title('Polarity Distribution', fontsize=14, fontweight='bold')
        ax3.set_xlabel('Polarity Score')
        ax3.set_ylabel('Frequency')
        ax3.grid(True, alpha=0.3)
        
        # 4. Subjectivity vs Polarity scatter
        subjectivities = [s['subjectivity'] for s in analysis_result['sentence_details']]
        scatter = ax4.scatter(subjectivities, polarities, alpha=0.6, c=polarities, 
                            cmap='RdYlGn', s=10)
        ax4.set_title('Subjectivity vs Polarity', fontsize=14, fontweight='bold')
        ax4.set_xlabel('Subjectivity (0 to 1)')
        ax4.set_ylabel('Polarity (-1 to 1)')
        ax4.grid(True, alpha=0.3)
        plt.colorbar(scatter, ax=ax4, label='Polarity')
        
        plt.tight_layout()
        
        # Save the chart
        chart_filename = f'sentiment_analysis_{video_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        chart_path = os.path.join(app.config['UPLOAD_FOLDER'], chart_filename)
        plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        chart_urls['combined'] = f'/static/{chart_filename}'
        
    except Exception as e:
        print(f"Error creating charts: {e}")
        chart_urls['error'] = str(e)
    
    return chart_urls

@app.route('/static/<filename>')
def serve_static(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)