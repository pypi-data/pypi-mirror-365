##################################################################################
##  OpenAI.fm TTS Provider                                                     ##
##################################################################################
import time
import requests
import pathlib
import tempfile
from io import BytesIO
from webscout import exceptions
from webscout.litagent import LitAgent
from concurrent.futures import ThreadPoolExecutor, as_completed
from webscout.Provider.TTS import utils
from webscout.Provider.TTS.base import BaseTTSProvider

class OpenAIFMTTS(BaseTTSProvider):
    """
    Text-to-speech provider using the OpenAI.fm API.
    """
    # Request headers
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "sec-fetch-dest": "audio",
        "sec-fetch-mode": "no-cors",
        "sec-fetch-site": "same-origin",
        "user-agent": LitAgent().random(),
        "referer": "https://www.openai.fm"
    }
    
    # Available voices with their IDs
    all_voices = {
        # OpenAI.fm voices
        "Alloy": "alloy",  # Neutral voice with balanced tone
        "Ash": "ash",      # Calm and thoughtful male voice
        "Ballad": "ballad", # Soft and melodic voice
        "Coral": "coral",   # Warm and inviting female voice
        "Echo": "echo",     # Clear and precise voice
        "Fable": "fable",   # Authoritative and narrative voice
        "Onyx": "onyx",     # Deep and resonant male voice
        "Nova": "nova",     # Energetic and bright female voice
        "Sage": "sage",     # Measured and contemplative voice
        "Shimmer": "shimmer", # Bright and optimistic voice
        "Verse": "verse"     # Melodic and rhythmic voice
    }

    def __init__(self, timeout: int = 20, proxies: dict = None):
        """Initializes the OpenAI.fm TTS client."""
        super().__init__()
        self.api_url = "https://www.openai.fm/api/generate"
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        if proxies:
            self.session.proxies.update(proxies)
        self.timeout = timeout

    def tts(self, text: str, voice: str = "Coral", instructions: str = None, verbose: bool = True) -> str:
        """
        Converts text to speech using the OpenAI.fm API and saves it to a file.

        Args:
            text (str): The text to convert to speech
            voice (str): The voice to use for TTS (default: "Coral")
            instructions (str): Voice instructions/prompt (default: "A cheerful guide. Friendly, clear, and reassuring.")
            verbose (bool): Whether to print debug information (default: True)

        Returns:
            str: Path to the generated audio file

        Raises:
            exceptions.FailedToGenerateResponseError: If there is an error generating or saving the audio.
        """
        # Validate input parameters
        if not text or not isinstance(text, str):
            raise ValueError("Text input must be a non-empty string")
        if len(text) > 10000:  # Add reasonable length limit
            raise ValueError("Text input exceeds maximum allowed length")
            
        assert (
            voice in self.all_voices
        ), f"Voice '{voice}' not one of [{', '.join(self.all_voices.keys())}]"

        with tempfile.NamedTemporaryFile(suffix=".mp3", dir=self.temp_dir, delete=False) as temp_file:
            filename = pathlib.Path(temp_file.name)
        voice_id = self.all_voices[voice]
        
        if instructions is None:
            instructions = "A cheerful guide. Friendly, clear, and reassuring."
            
        # Prepare parameters for the API request
        params = {
            "input": text,
            "prompt": instructions,
            "voice": voice_id
        }

        try:
            # Make the API request
            response = self.session.get(
                self.api_url,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Save the audio file
            with open(filename, "wb") as f:
                f.write(response.content)
                
            if verbose:
                print(f"[debug] Audio saved to {filename}")
                
            return filename.as_posix()
            
        except requests.exceptions.RequestException as e:
            if verbose:
                print(f"[debug] Failed to perform the operation: {e}")
            raise exceptions.FailedToGenerateResponseError(
                f"Failed to perform the operation: {e}"
            )
if __name__ == "__main__":
    # Example usage
    tts_provider = OpenAIFMTTS()
    try:
        audio_file = tts_provider.tts("Hello, this is a test.", instructions="A cheerful guide. Friendly, clear, and reassuring.", voice="Coral")
        print(f"Audio file generated: {audio_file}")
    except exceptions.FailedToGenerateResponseError as e:
        print(f"Error: {e}")