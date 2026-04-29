"""
Voice · Text-to-speech output.

OWNER: [TBD at kickoff]
BRANCH: voice-ux

Uses the browser's built-in SpeechSynthesis API via a small HTML snippet
embedded in Streamlit. This is free (no API costs) and runs client-side.

For a more polished-sounding voice, you could swap this for ElevenLabs
or OpenAI TTS API — but the browser voice is reliable enough for a
class demo and has zero cost/latency per call.

What you need to do:

1. Confirm browser SpeechSynthesis works in the team's demo browser
   (Chrome and Edge are reliable; Safari is flaky; Firefox depends on OS).
2. Decide if you want auto-speak (speaks immediately when text arrives)
   or button-triggered (user clicks to hear it).
3. If auto-speak causes demo-day weirdness, use button-triggered.
"""

import streamlit as st
import streamlit.components.v1 as components
import json


def speak_button(text: str) -> None:
    """
    Render a "🔊 Hear the explanation" button. Clicking it speaks the
    text via the browser's built-in speech synthesis.

    Args:
        text: The text to speak when the button is clicked.
    """
    # We escape the text for safe embedding in JS
    escaped = json.dumps(text)

    html = f"""
    <div style="margin: 10px 0;">
      <button
        id="speak-btn"
        onclick="speakText()"
        style="
          background: #ff4b4b;
          color: white;
          border: none;
          padding: 10px 20px;
          border-radius: 6px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
        ">
        🔊 Hear the explanation
      </button>
      <button
        id="stop-btn"
        onclick="stopSpeaking()"
        style="
          background: #6c757d;
          color: white;
          border: none;
          padding: 10px 20px;
          border-radius: 6px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
          margin-left: 8px;
        ">
        ⏹️ Stop
      </button>
    </div>

    <script>
      function speakText() {{
        if ('speechSynthesis' in window) {{
          window.speechSynthesis.cancel();
          const utterance = new SpeechSynthesisUtterance({escaped});
          utterance.rate = 1.0;
          utterance.pitch = 1.0;
          utterance.volume = 1.0;
          window.speechSynthesis.speak(utterance);
        }} else {{
          alert('Your browser does not support speech synthesis. Try Chrome or Edge.');
        }}
      }}

      function stopSpeaking() {{
        if ('speechSynthesis' in window) {{
          window.speechSynthesis.cancel();
        }}
      }}
    </script>
    """

    components.html(html, height=70)


def speak_auto(text: str) -> None:
    """
    Speak text automatically without a button click. Use this when you
    want the agent to feel truly conversational. Warning: can be jarring
    if the user didn't expect sound.

    Args:
        text: The text to speak immediately when this component renders.
    """
    escaped = json.dumps(text)
    html = f"""
    <script>
      if ('speechSynthesis' in window) {{
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance({escaped});
        utterance.rate = 1.0;
        window.speechSynthesis.speak(utterance);
      }}
    </script>
    """
    components.html(html, height=0)
