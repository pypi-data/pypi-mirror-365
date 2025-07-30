function showElementById(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.display = 'block';
    } else {
        console.error(`[HTMLInjector] Helper Error: Element with ID '${elementId}' was not found in the DOM.`);
    }
}


function hideElementById(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.display = 'none';
    } else {
        console.error(`[HTMLInjector] Helper Error: Element with ID '${elementId}' was not found in the DOM.`);
    }
}