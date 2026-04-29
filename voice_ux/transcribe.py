"""
Voice · Speech-to-text transcription.

OWNER: [TBD at kickoff — likely Alex double-hat]
BRANCH: voice-ux

Uses streamlit-mic-recorder to capture audio from the browser, then
Whisper (OpenAI API) to transcribe. Transcripts are passed to the parser
which extracts structured profile fields.

What you need to do:

1. Render the mic recorder in the Streamlit UI.
2. When audio is captured, send it to Whisper.
3. Pass the transcript through `parser.parse_profile_from_transcript`.
4. If the parser can't find all required fields, ask follow-up questions
   via speak() + mic recorder (this is the "conversational" part).

Stub behavior: returns None until the user records audio. If no OpenAI
key is set, shows a clear message rather than crashing.
"""

import os
import io

# TODO: from openai import OpenAI
# TODO: from streamlit_mic_recorder import mic_recorder
import streamlit as st

from voice_ux.parser import parse_profile_from_transcript


def transcribe_profile() -> dict | None:
    """
    Record audio from the browser, transcribe via Whisper, and parse
    into a structured profile dict.

    Returns:
        dict with profile fields if capture + parse succeeded, else None.
    """
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        st.warning(
            "🎤 Voice mode needs an OpenAI API key for Whisper transcription. "
            "Switch to Keyboard mode in the sidebar, or ask Alex for the key."
        )
        return None

    # TODO: from streamlit_mic_recorder import mic_recorder
    # TODO: audio = mic_recorder(
    #           start_prompt="🎤 Click to record your profile",
    #           stop_prompt="⏹️ Stop recording",
    #           just_once=False,
    #           use_container_width=True,
    #           key="profile_recorder",
    #       )
    #
    # TODO: if audio is None:
    # TODO:     return None  # user hasn't recorded yet
    #
    # TODO: # audio['bytes'] is the WAV bytes
    # TODO: client = OpenAI(api_key=api_key)
    # TODO: audio_file = io.BytesIO(audio['bytes'])
    # TODO: audio_file.name = "recording.wav"
    # TODO:
    # TODO: transcript = client.audio.transcriptions.create(
    # TODO:     model=os.getenv("WHISPER_MODEL", "whisper-1"),
    # TODO:     file=audio_file,
    # TODO: )
    # TODO:
    # TODO: st.caption(f"📝 Heard: \"{transcript.text}\"")
    # TODO:
    # TODO: profile, missing = parse_profile_from_transcript(transcript.text)
    # TODO:
    # TODO: if missing:
    # TODO:     # Re-prompt for missing fields — this is the conversational part
    # TODO:     st.info(f"I didn't catch your {', '.join(missing)}. Please record again or switch to keyboard.")
    # TODO:     return None
    # TODO:
    # TODO: return profile

    # --- STUB ---
    st.info(
        "🎤 Voice transcription stub — not yet implemented. "
        "Owner: [TBD] · Branch: voice-ux"
    )
    st.caption("Switch to Keyboard mode in the sidebar to use the app end-to-end.")
    return None
