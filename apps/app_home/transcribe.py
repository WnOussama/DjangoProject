import os
from typing import Optional


def transcribe_video(file_path: str) -> Optional[str]:
    """
    Try to transcribe a video/audio file using OpenAI Whisper API if OPENAI_API_KEY is set
    and the openai package is available. Returns transcript text or None.
    Also prints what happens for debug purposes.
    """
    print(f"[AI Transcript] Trying to transcribe: {file_path}")
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("[AI Transcript] No OPENAI_API_KEY set in .env or environment.")
            return None
        import openai  # type: ignore
        # Both old and new SDKs exist in the wild; support legacy usage
        try:
            print("[AI Transcript] Using OpenAI Python client...")
            client = openai.OpenAI(api_key=api_key)  # new sdk
            with open(file_path, "rb") as f:
                print("[AI Transcript] Sending file to Whisper... (new api)")
                resp = client.audio.transcriptions.create(model="whisper-1", file=f)
                print(f"[AI Transcript] API response: {str(resp)[:140]}")
                return getattr(resp, "text", None)
        except Exception as err:
            print(f"[AI Transcript] Falling back to old openai API (error: {err})")
            openai.api_key = api_key  # legacy
            with open(file_path, "rb") as f:
                resp = openai.Audio.transcribe("whisper-1", f)
                print(f"[AI Transcript] API response (legacy): {str(resp)[:140]}")
                return resp.get("text")
    except Exception as exc:
        print(f"[AI Transcript] ERROR: {str(exc)[:400]}")
        return None


def summarize_text(text: str) -> Optional[str]:
    """
    Summarizes the given text using Hugging Face transformers' pipeline.
    Also prints what happens for debug purposes.
    """
    print("[AI Summarizer] Attempting to summarize text...")
    try:
        from transformers import pipeline  # type: ignore
        summarizer = pipeline("summarization")
        print(f"[AI Summarizer] Original text length: {len(text)}")
        summary_list = summarizer(text, max_length=130, min_length=30, do_sample=False)
        summary_text = summary_list[0]['summary_text'] if summary_list else None
        print(f"[AI Summarizer] Summary: {summary_text}")
        return summary_text
    except ImportError:
        print("[AI Summarizer] transformers library not installed. Run 'pip install transformers'.")
    except Exception as e:
        print(f"[AI Summarizer] ERROR: {str(e)[:400]}")
    return None


def sentiment_analysis(text: str):
    try:
        from textblob import TextBlob
        print(f"[AI Sentiment] Analyzing: {text}")
        result = TextBlob(text).sentiment
        print(f"[AI Sentiment] Result: polarity={result.polarity}, subjectivity={result.subjectivity}")
        return {'polarity': result.polarity, 'subjectivity': result.subjectivity}
    except ImportError:
        print("[AI Sentiment] textblob not installed. Run 'pip install textblob'")
        return None
    except Exception as e:
        print(f"[AI Sentiment] ERROR: {str(e)}")
        return None


