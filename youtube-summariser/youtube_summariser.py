from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline

def get_transcript(video_id):
    """Fetches the transcript of a YouTube video."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = ' '.join([entry['text'] for entry in transcript])
        return text
    except Exception as e:
        print(f"Error getting transcript: {e}")
        return None

# def summarize_text(text):
#     """Summarizes the input text using a pre-trained model."""
#     summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
#     try:
#         summary = summarizer(text, max_length=60, min_length=30, do_sample=False)  #Adjust Max Length to increase summary size
#         return summary[0]['summary_text']
#     except Exception as e:
#         print(f"Error during summarization: {e}")
#         return None
    
def summarize_text(text, chunk_size=5000):  # Adjust chunk_size
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")  # Or smaller model
    print(len(text))
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    summaries = []
    for chunk in chunks:
        try:
            summary = summarizer(chunk, max_length=130, min_length=100, do_sample=False)  # Adjust max_length
            summaries.append(summary[0]['summary_text'])
        except Exception as e:
            print(f"Error summarizing chunk: {e}")
            return None

    # Combine the chunk summaries (can use another summarization pass here)
    combined_summary = ' '.join(summaries)
    if len(summaries) > 1:
        try:
            print(len(combined_summary))
            print('\ncombined summary:')
            
            print(combined_summary)
            final_summary = summarizer(combined_summary, max_length=5000, min_length=2000, do_sample=False)
            print('final summary') # Or smaller model
            return final_summary[0]['summary_text']
        except:
            print("exception combined")
            return combined_summary
    else:
        print("length is not > 1")
        return combined_summary

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

if __name__ == "__main__":
    youtube_url = input("Enter YouTube video URL: ")
    video_id = get_video_id(youtube_url)

    if not video_id:
        print("Invalid YouTube URL.")
        exit()

    transcript = get_transcript(video_id)
    # print(transcript)

    if transcript:
        summary = summarize_text(transcript)

        if summary:
            print("\nSummary:")
            print(summary)
        else:
            print("Failed to generate summary.")
    else:
        print("Could not retrieve transcript.")

        