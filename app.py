import os
import sys
from typing import Union, Literal

import gradio as gr
import tempfile

from openai import OpenAI

server_name = os.getenv("SERVER_NAME", "127.0.0.1")
openai_key = os.environ.get("OPENAI_API_KEY")

def tts(
        text: str,
        model: Union[str, Literal["tts-1", "tts-1-hd"]],
        voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
        output_file_format: Literal["mp3", "opus", "aac", "flac"] = "mp3",
        speed: float = 1.0
):
    if len(text) > 0:
        try:
            client = OpenAI(api_key=openai_key)

            response = client.audio.speech.create(
                model=model,
                voice=voice,
                input=text,
                response_format=output_file_format,
                speed=speed
            )

        except Exception as error:
            print(str(error))
            raise gr.Error(
                "An error occurred while generating speech. Please check your API key and come back try again.")

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            temp_file.write(response.content)

        temp_file_path = temp_file.name

        return temp_file_path
    else:
        return "1-second-of-silence.mp3"


with gr.Blocks() as demo:
    gr.Markdown("# <center> OpenAI Text-To-Speech API with Gradio </center>")
    with gr.Row(variant="panel"):
        model = gr.Dropdown(choices=["tts-1", "tts-1-hd"], label="Model", value="tts-1")
        voice = gr.Dropdown(choices=["alloy", "echo", "fable", "onyx", "nova", "shimmer"], label="Voice Options",
                            value="alloy")
        output_file_format = gr.Dropdown(choices=["mp3", "opus", "aac", "flac"], label="Output Options", value="mp3")
        speed = gr.Slider(minimum=0.25, maximum=4.0, value=1.0, step=0.01, label="Speed")

    text = gr.Textbox(label="Input text",
                      placeholder="Enter your text and then click on the \"Text-To-Speech\" button, "
                                  "or simply press the Enter key.")
    btn = gr.Button("Text-To-Speech")
    output_audio = gr.Audio(label="Speech Output")

    text.submit(fn=tts, inputs=[text, model, voice, output_file_format, speed], outputs=output_audio, api_name="tts")
    btn.click(fn=tts, inputs=[text, model, voice, output_file_format, speed], outputs=output_audio, api_name=False)

demo.launch(server_name=server_name)

# curl --location "http://127.0.0.1:7860/api/tts" \
# --header "Content-Type: application/json" \
# --data "{"data":["Hello", "tts-1", "alloy"]}"

# curl --location "http://127.0.0.1:7860/file=/private/var/folders/5v/
# 0b0l_t1x3752h3t1bt_rtnjr0000gn/T/gradio/e91d8bf36ee07f536bed6b5a5bf9522b1fc86436/tmpkem8ubvz.mp3"