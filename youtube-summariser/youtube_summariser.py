from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline
import requests
import json

def get_transcript(video_id):
    """Fetches the transcript of a YouTube video."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = ' '.join([entry['text'] for entry in transcript])
        return text
    except Exception as e:
        print(f"Error getting transcript: {e}")
        return None

def summarize_text(text, chunk_size=5000, overlap_size=500):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    chunks = []
    i = 0
    while i < len(text):
        chunks.append(text[i:i + chunk_size])
        i += chunk_size - overlap_size  # Move forward, accounting for overlap

    summaries = []
    for chunk in chunks:
        try:
            summary = summarizer(chunk, max_length=130, min_length=100, do_sample=False)
            summaries.append(summary[0]['summary_text'])
        except Exception as e:
            print(f"Error summarizing chunk: {e}")
            return None
        
    # Combine the chunk summaries (more intelligently)
    combined_summary = ' '.join(summaries)

    if len(summaries) > 1:
        try:
            print(len(combined_summary))
            print('\ncombined summary:')
            print(combined_summary)
            # Recursive Summarization
            final_summaries = []
            recursive_chunk_size = 1000  # adjust based on your model and GPU

            recursive_chunks = [combined_summary[i:i + recursive_chunk_size] for i in
                                range(0, len(combined_summary), recursive_chunk_size)]
            for r_chunk in recursive_chunks:
                final_summary = summarizer(r_chunk, max_length=1024, min_length=800, do_sample=False)
                final_summaries.append(final_summary[0]['summary_text'])

            return " ".join(final_summaries)

        except Exception as e:
            print(f"exception combined: {e}")
            return combined_summary
    else:
        print("length is not > 1")
        return combined_summary
    
# def summarize_text(text, chunk_size=5000):  # Adjust chunk_size
#     summarizer = pipeline("summarization", model="facebook/bart-large-cnn")  # Or smaller model
#     print(len(text))
#     chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
#     summaries = []
#     for chunk in chunks:
#         try:
#             summary = summarizer(chunk, max_length=130, min_length=100, do_sample=False)  # Adjust max_length
#             summaries.append(summary[0]['summary_text'])
#         except Exception as e:
#             print(f"Error summarizing chunk: {e}")
#             return None

#     # Combine the chunk summaries (can use another summarization pass here)
#     combined_summary = ' '.join(summaries)
#     if len(summaries) > 1:
#         try:
#             print(len(combined_summary))
#             print('\ncombined summary:')
            
#             print(combined_summary)
#             final_summary = summarizer(combined_summary, max_length=1024, min_length=1000, do_sample=False)
#             print('final summary') # Or smaller model
#             return final_summary[0]['summary_text']
#         except:
#             print("exception combined")
#             return combined_summary
#     else:
#         print("length is not > 1")
#         return combined_summary

def get_video_id(url):
    """Extracts the video ID from a YouTube URL."""
    from urllib.parse import urlparse, parse_qs

    parsed_url = urlparse(url)
    if parsed_url.netloc == 'www.youtube.com':
        query_params = parse_qs(parsed_url.query)
        if 'v' in query_params:
            return query_params['v'][0]
    elif parsed_url.netloc == 'youtu.be':
        return parsed_url.path[1:]  # Remove leading slash

    return None

def categorize_with_ollama(text):
    """Uses Ollama to categorize the content of the summary."""
    try:
        # Prepare the prompt for categorization
        prompt = f"""Please analyze this summary of transcript from a youtube video and provide:
        1. Divide the text into parts
        2. consider the parts are different chapters of the full content
        3. Key themes or topics (3-4 points) that was discussed or mentioned
        4. Make sure when you explain you use the word "video" for example:  This video talks about, This video discusses about . This way when the user read he understands that he is reading about summary of a video
       
        
        Text to analyze: {text}"""
        
        # Make request to Ollama
        response = requests.post('http://localhost:11434/api/generate',
                               json={
                                   "model": "mistral",
                                   "prompt": prompt,
                                   "stream": False
                               })
        
        if response.status_code == 200:
            return response.json()['response']
        else:
            return "Error: Could not connect to Ollama service"
            
    except Exception as e:
        return f"Error during categorization: {e}"

if __name__ == "__main__":
    youtube_url = input("Enter YouTube video URL: ")
    video_id = get_video_id(youtube_url)

    if not video_id:
        print("Invalid YouTube URL.")
        exit()

    transcript = get_transcript(video_id)

    if transcript:
        summary = summarize_text(transcript)

        if summary:
            print("\nSummary:")
            print(summary)
            
            print("\nAnalyzing content with Ollama...")
            categorization = categorize_with_ollama(summary)
            print("\nContent Analysis:")
            print(categorization)
        else:
            print("Failed to generate summary.")
    else:
        print("Could not retrieve transcript.")

        