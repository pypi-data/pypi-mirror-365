# demo/app.py

import gradio as gr
import time
from gradio_bottombar import BottomBar

def chat_response(message, history):
    history = history or ""
    history += f"You: {message}\n"
    time.sleep(1) # Simulate thinking
    history += f"Bot: Thanks for the message! You said: '{message}'\n"
    return history, ""

def update_label(value):
    return f"Current temperature is: {value}"

css = """
body {    
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;    
    margin: 0;
    padding: 0;
}
.gradio-container {    
    border-radius: 15px;
    padding: 30px 40px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
    margin: 40px 340px;    
}
.gradio-container h1 {    
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
}
.fillable {
    width: 100% !important;
    max-width: unset !important;
}
#examples_container {
    margin: auto;
    width: 90%;
}
#examples_row {
    justify-content: center;
}
#tips_row{    
    padding-left: 20px;
}
.sidebar {    
    border-radius: 10px;
    padding: 10px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}
.sidebar .toggle-button {    
    background: linear-gradient(90deg, #34d399, #10b981) !important;
    border: none;    
    padding: 12px 18px;
    text-transform: uppercase;
    font-weight: bold;
    letter-spacing: 1px;
    border-radius: 5px;
    cursor: pointer;
    transition: transform 0.2s ease-in-out;
}
.toggle-button:hover {
    transform: scale(1.05);
}
.bottom-bar {    
    border-radius: 10px;
    padding: 10px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}
.bottom-bar .toggle-bottom-button {    
    background: linear-gradient(90deg, #34d399, #10b981) !important;
    border: none;        
    text-transform: uppercase;
    font-weight: bold;
    letter-spacing: 1px;    
    cursor: pointer;    
}

"""

with gr.Blocks(css=css, theme=gr.themes.Ocean(), title="Full Layout Demo") as demo:
    gr.Markdown(
        """
        # Full Layout Demo: BottomBar with Sidebars
        This demo shows the `BottomBar` with `bring_to_front=True`. Notice how it now renders
        **on top of** the sidebars when they overlap.
        """
    )

    with BottomBar(open=True, height=180, bring_to_front=True):
        with gr.Row():
            message_box = gr.Textbox(
                show_label=False,
                placeholder="Type your message here...",
                elem_id="message-input",
                scale=7
            )
            send_button = gr.Button("Send", variant="primary", scale=1)
        with gr.Row():
            gr.Button("Upload File")
            gr.Button("Record Audio")
            gr.ClearButton([message_box])

    with gr.Row(equal_height=True):
        with gr.Sidebar(position="left"):
            gr.Markdown("### ⚙️ Settings")
            model_temp = gr.Slider(0, 1, value=0.7, label="Model Temperature")
            temp_label = gr.Markdown(update_label(0.7))
            gr.CheckboxGroup(
                ["Enable History", "Use Profanity Filter", "Stream Response"],
                label="Chat Options",
                value=["Enable History", "Stream Response"]
            )

        with gr.Column(scale=3):
            gr.Markdown("### 🤖 Chat Interface")
            chatbot_display = gr.Textbox(
                label="Chat History",
                lines=25,
                interactive=False
            )

        with gr.Sidebar(position="right"):
            gr.Markdown("### ℹ️ Information")
            gr.Radio(
                ["GPT-4", "Claude 3", "Llama 3"],
                label="Current Model",
                value="Claude 3"
            )
            gr.Dropdown(
                ["English", "Spanish", "Portuguese"],
                label="Language",
                value="Portuguese"
            )
    
    send_button.click(
        fn=chat_response,
        inputs=[message_box, chatbot_display],
        outputs=[chatbot_display, message_box]
    )
    message_box.submit(
        fn=chat_response,
        inputs=[message_box, chatbot_display],
        outputs=[chatbot_display, message_box]
    )
    model_temp.change(
        fn=update_label,
        inputs=model_temp,
        outputs=temp_label
    )

if __name__ == "__main__":
    demo.launch()