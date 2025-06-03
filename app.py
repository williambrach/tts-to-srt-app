import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncAzureOpenAI

# Import gradio after other imports to avoid conflicts
import gradio as gr

# Load environment variables
load_dotenv()

# Initialize Azure OpenAI client
API_KEY = os.getenv("API_KEY")
API_BASE = os.getenv("API_BASE")

azure = AsyncAzureOpenAI(
    azure_endpoint=API_BASE,
    api_key=API_KEY,
    api_version="2025-03-01-preview",
)

async def generate_audio_file(input_text, output_path, voice_name="coral", instructions=None):
    """Generate audio file from Azure OpenAI TTS and save to the given path"""
    async with azure.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice=voice_name,
        input=input_text,
        instructions=instructions,
        response_format="mp3",
    ) as response:
        await response.stream_to_file(output_path)

async def generate_srt_file(input_file_path, output_path, language="en"):
    """Generate SRT subtitle file from audio using Whisper"""
    with open(input_file_path, "rb") as audio_file:
        try:
            transcription = await azure.audio.transcriptions.create(
                file=audio_file,
                language=language,
                model="whisper",
                response_format="srt",
            )
            with open(output_path, "w", encoding="utf-8") as srt_file:
                srt_file.write(transcription)
        except Exception as e:
            raise Exception(f"Transcription error: {e}")

def process_text_to_speech_and_srt(text, voice, instructions, language):
    """Main function to process text through TTS and generate SRT"""
    if not text.strip():
        return None, None, "Please enter some text to convert."
    
    try:
        # Create output file paths
        mp3_path = "output.mp3"
        srt_path = "output.srt"
        
        # Run async functions
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Generate audio
        loop.run_until_complete(generate_audio_file(
            input_text=text,
            output_path=mp3_path,
            voice_name=voice,
            instructions=instructions if instructions.strip() else None
        ))
        
        # Generate SRT
        loop.run_until_complete(generate_srt_file(
            input_file_path=mp3_path,
            output_path=srt_path,
            language=language
        ))
        
        loop.close()
        
        # Read SRT content for display
        with open(srt_path, "r", encoding="utf-8") as f:
            srt_content = f.read()
        
        return mp3_path, srt_content, "✅ Audio and subtitles generated successfully!"
        
    except Exception as e:
        return None, None, f"❌ Error: {str(e)}"

# Define the Gradio interface
with gr.Blocks(title="TTS & Transcription App") as app:
    gr.Markdown("# 🎤 Text-to-Speech & Transcription App")
    gr.Markdown("Convert text to speech with custom voice instructions, then generate subtitles.")
    
    with gr.Row():
        with gr.Column(scale=2):
            # Input section
            text_input = gr.Textbox(
                label="Text to Convert",
                placeholder="Enter the text you want to convert to speech...",
                lines=6,
                value="""Thank you for reaching out, and I'm truly sorry about the unexpected charge on your bill. I completely understand how frustrating this must be, especially after your stay.

After reviewing your reservation, I can confirm that this was an error on our part. I'll be issuing a full refund right away, and you should see the amount credited to your payment method within a few business days.

I appreciate your understanding and patience, and I'm here if you need any further assistance. Thank you for allowing us to resolve this for you."""
            )
            
            voice_dropdown = gr.Dropdown(
                label="Voice",
                choices=["alloy", "echo", "fable", "onyx", "nova", "shimmer", "coral"],
                value="coral"
            )
            
            language_dropdown = gr.Dropdown(
                label="Language (for transcription)",
                choices=["sk","en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh"],
                value="sk"
            )
            
            instructions_input = gr.Textbox(
                label="Voice Instructions (Optional)",
                placeholder="Describe how the voice should sound...",
                lines=4,
                value="""Voice Affect: Calm, composed, and reassuring. Competent and in control, instilling trust.

Tone: Sincere, empathetic, with genuine concern for the customer and understanding of the situation.

Pacing: Slower during the apology to allow for clarity and processing. Faster when offering solutions to signal action and resolution.

Emotions: Calm reassurance, empathy, and gratitude.

Pronunciation: Clear, precise: Ensures clarity, especially with key details. Focus on key words like "refund" and "patience."

Pauses: Before and after the apology to give space for processing the apology."""
            )
            
            generate_btn = gr.Button("🎵 Generate Audio & Subtitles", variant="primary")
        
        with gr.Column(scale=2):
            # Output section
            status_output = gr.Textbox(label="Status", interactive=False)
            audio_output = gr.Audio(label="Generated Audio")
            srt_output = gr.Textbox(
                label="Generated Subtitles (SRT)",
                lines=10,
                interactive=False
            )
    
    # Connect the button to the processing function
    generate_btn.click(
        fn=process_text_to_speech_and_srt,
        inputs=[text_input, voice_dropdown, instructions_input, language_dropdown],
        outputs=[audio_output, srt_output, status_output]
    )
    
    gr.Markdown("""
    ### Instructions:
    1. Enter your text in the text box
    2. Choose a voice from the dropdown
    3. Optionally add voice instructions for tone, pacing, etc.
    4. Select the language for transcription
    5. Click "Generate Audio & Subtitles"
    
    The app will generate an MP3 audio file and corresponding SRT subtitle file.
    """)

if __name__ == "__main__":
    app.launch(share=False, server_name="0.0.0.0", server_port=8888)