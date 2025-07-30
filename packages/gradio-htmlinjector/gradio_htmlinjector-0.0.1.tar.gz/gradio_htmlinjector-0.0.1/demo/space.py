
import gradio as gr
from app import demo as app
import os

_docs = {'HTMLInjector': {'description': 'An invisible Gradio component to inject custom assets into the application.\nIt can inject:\n- CSS styles and JavaScript code into the <head>.\n- HTML content into the end of the <body>.\nIt is populated via the Blocks.load() event.', 'members': {'__init__': {}, 'postprocess': {'value': {'type': 'typing.Optional[typing.Dict[str, str]][\n    typing.Dict[str, str][str, str], None\n]', 'description': None}}, 'preprocess': {'return': {'type': 'Any', 'description': None}, 'value': None}}, 'events': {}}, '__meta__': {'additional_interfaces': {}, 'user_fn_refs': {'HTMLInjector': []}}}

abs_path = os.path.join(os.path.dirname(__file__), "css.css")

with gr.Blocks(
    css=abs_path,
    theme=gr.themes.Default(
        font_mono=[
            gr.themes.GoogleFont("Inconsolata"),
            "monospace",
        ],
    ),
) as demo:
    gr.Markdown(
"""
# `gradio_htmlinjector`

<div style="display: flex; gap: 7px;">
<img alt="Static Badge" src="https://img.shields.io/badge/version%20-%200.0.1%20-%20orange">  
</div>

An HTML, JS, and CSS element injector
""", elem_classes=["md-custom"], header_links=True)
    app.render()
    gr.Markdown(
"""
## Installation

```bash
pip install gradio_htmlinjector
```

## Usage

```python
import gradio as gr
from gradio_htmlinjector import HTMLInjector

def inject_all_assets():
    \"\"\"
    This function prepares the payload of CSS, JS, and HTML content.
    It's called by the demo.load() event listener.
    \"\"\"
    css_code = ""
    js_code = ""
    
    # Define the HTML for a floating popup, initially hidden.
    popup_html = \"\"\"
    <div id="my-floating-popup" style="display: none; position: fixed; top: 20%; left: 50%; transform: translateX(-50%); z-index: 9999; background: var(--panel-background-fill, white); border: 1px solid var(--border-color-primary); padding: 25px; border-radius: var(--radius-lg); box-shadow: var(--shadow-drop-lg);">
        <h2>Injected HTML Popup</h2>
        <p>This content exists outside the main Gradio layout.</p>
        <br>
        <button class="lg primary svelte-1ixn6qd" onclick="hideElementById('my-floating-popup')">
            Close Me
        </button>
    </div>
    \"\"\"

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
    show_popup_js = \"\"\"
    () => {
        const action = () => showElementById('my-floating-popup');

        if (typeof showElementById === 'function') {
            action();
        } else {
            console.log("[Button Click] Helpers not ready, waiting for 'assets-injected' event...");
            document.addEventListener('assets-injected', action, { once: true });
        }
    }
    \"\"\"
    
    show_popup_button.click(fn=None, inputs=None, outputs=None, js=show_popup_js)

    demo.load(fn=inject_all_assets, inputs=None, outputs=[html_injector])


if __name__ == '__main__':
    demo.launch()
```
""", elem_classes=["md-custom"], header_links=True)


    gr.Markdown("""
## `HTMLInjector`

### Initialization
""", elem_classes=["md-custom"], header_links=True)

    gr.ParamViewer(value=_docs["HTMLInjector"]["members"]["__init__"], linkify=[])




    gr.Markdown("""

### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.



 ```python
def predict(
    value: Any
) -> typing.Optional[typing.Dict[str, str]][
    typing.Dict[str, str][str, str], None
]:
    return value
```
""", elem_classes=["md-custom", "HTMLInjector-user-fn"], header_links=True)




    demo.load(None, js=r"""function() {
    const refs = {};
    const user_fn_refs = {
          HTMLInjector: [], };
    requestAnimationFrame(() => {

        Object.entries(user_fn_refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}-user-fn`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })

        Object.entries(refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })
    })
}

""")

demo.launch()
