<script lang="ts">
    import { Block } from "@gradio/atoms";
    import { onMount } from "svelte";

    /**
     * @prop {object | undefined} value - The payload received from the backend.
     * It can contain 'js', 'css', and 'body_html' string properties.
     */
    export let value;

    // A local variable to temporarily store the HTML payload.
    let htmlToInject: string | null = null;
    
    // A flag to ensure the body injection only happens once.
    let bodyInjected = false;

    /**
     * This function safely injects the HTML content into the document body.
     * It is separated to ensure it can be called reliably after the component has mounted.
     */
    function injectBodyHTML() {
        // Proceed only if there is HTML to inject and it hasn't been injected yet.
        if (htmlToInject && !bodyInjected) {
            const body = document.body;
            const htmlContainerId = 'gradio-custom-body-html-container';
            
            // Double-check that the container doesn't already exist.
            if (!document.getElementById(htmlContainerId)) {
                console.log("[HTMLInjector] Injecting HTML content into the body.");
                const container = document.createElement('div');
                container.id = htmlContainerId;
                container.innerHTML = htmlToInject;
                body.appendChild(container);

                // Set the flag to true to prevent future injections.
                bodyInjected = true;
            }
        }
    }

    // `onMount` runs only once, after the component has been rendered to the DOM.
    // This guarantees that `document.body` is fully available and ready for manipulation.
    onMount(() => {
        // If the 'value' prop was already received before mounting, `htmlToInject` will have content.
        // This call ensures it gets injected now that the DOM is ready.
        injectBodyHTML();
    });

    /**
     * The reactive statement is still necessary to capture the `value` update
     * from the `demo.load()` event, which happens after the initial mount.
     */
    $: {
        if (value) {
            const head = document.head;

            // --- CSS and JS injection can remain here, as the <head> is less sensitive ---
            if (value.css) {
                const styleId = 'gradio-custom-head-styles';
                if (!document.getElementById(styleId)) {
                    const styleElement = document.createElement('style');
                    styleElement.id = styleId;
                    styleElement.innerHTML = value.css;
                    head.appendChild(styleElement);
                }
            }
            if (value.js) {
                const scriptId = 'gradio-custom-head-script';
                if (!document.getElementById(scriptId)) {
                    const scriptElement = document.createElement('script');
                    scriptElement.id = scriptId;
                    scriptElement.innerHTML = value.js;
                    head.appendChild(scriptElement);
                }
            }
            
            if (value.body_html) {
                // Store the HTML payload in our local variable.
                htmlToInject = value.body_html;
                // Attempt to inject. This will only succeed if onMount has already run
                // and `bodyInjected` is still false.
                injectBodyHTML();
            }
        }
    }
</script>

<!-- The rest of your component remains the same -->
<div class="hidden-wrapper">
    <Block style="border-width: 0 !important; padding: 0 !important; margin: 0 !important;">
        <!-- This Block is required for the component to register correctly -->
    </Block>
</div>

<style>
   .hidden-wrapper {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        border: none !important;
        position: absolute;
    }
</style>