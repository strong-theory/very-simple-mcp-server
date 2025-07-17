from youtube_transcript_api import YouTubeTranscriptApi

ytt_api = YouTubeTranscriptApi()

def download(video_id: str) -> str:
    fetched_transcript = ytt_api.fetch(video_id)
    result = [snippet.text for snippet in fetched_transcript]
    return "".join(result)
