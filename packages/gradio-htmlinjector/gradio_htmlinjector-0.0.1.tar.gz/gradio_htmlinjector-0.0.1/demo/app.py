import gradio as gr
from gradio_htmlinjector import HTMLInjector

def inject_all_assets():
    """
    This function prepares the payload of CSS, JS, and HTML content.
    It's called by the demo.load() event listener.
    """
    css_code = ""
    js_code = ""
    
    # Define the HTML for a floating popup, initially hidden.
    popup_html = """
    <div id="my-floating-popup" style="display: none; position: fixed; top: 20%; left: 50%; transform: translateX(-50%); z-index: 9999; background: var(--panel-background-fill, white); border: 1px solid var(--border-color-primary); padding: 25px; border-radius: var(--radius-lg); box-shadow: var(--shadow-drop-lg);">
        <h2>Injected HTML Popup</h2>
        <p>This content exists outside the main Gradio layout.</p>
        <br>
        <button class="lg primary svelte-1ixn6qd" onclick="hideElementById('my-floating-popup')">
            Close Me
        </button>
    </div>
    """

    # Load JavaScript helper functions from an external file.
    try:
        with open("custom_script.js", "r", encoding="utf-8") as f:
            js_code += f.read() + "\n"
    except FileNotFoundError as e:
        print(f"Info: 'custom_script.js' file not found: {e}")

    # Load custom styles from an external file.
    try:
        with open("custom_styles.css", "r", encoding="utf-8") as f:
            css_code += f.read() + "\n"
    except FileNotFoundError as e:
        print(f"Info: 'custom_styles.css' file not found: {e}")

    return {"css": css_code, "js": js_code, "body_html": popup_html}


with gr.Blocks() as demo:
    gr.Markdown("# HTMLInjector Component Demo")
    gr.Markdown("This demo uses a custom component to inject a floating HTML popup and its controlling JavaScript.")
    
    html_injector = HTMLInjector()
    
    show_popup_button = gr.Button("Show Injected Popup", variant="primary")
    
    # This intelligent JS snippet solves the race condition.
    # It defines the action to perform, checks if the helper function is ready,
    # and if not, it waits for the custom 'assets-injected' event before proceeding.
    show_popup_js = """
    () => {
        const action = () => showElementById('my-floating-popup');

        if (typeof showElementById === 'function') {
            action();
        } else {
            console.log("[Button Click] Helpers not ready, waiting for 'assets-injected' event...");
            document.addEventListener('assets-injected', action, { once: true });
        }
    }
    """
    
    show_popup_button.click(fn=None, inputs=None, outputs=None, js=show_popup_js)

    demo.load(fn=inject_all_assets, inputs=None, outputs=[html_injector])


if __name__ == '__main__':
    demo.launch()