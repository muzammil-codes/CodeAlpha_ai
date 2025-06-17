// to get references to all the necessary HTML elements
const sourceLanguageSelect = document.getElementById('source-language');
const targetLanguageSelect = document.getElementById('target-language');
const sourceTextarea = document.getElementById('source-text');
const translatedTextarea = document.getElementById('translated-text');
const translateButton = document.getElementById('translate-btn');
const copyButton = document.getElementById('copy-btn');
const speakButton = document.getElementById('speak-btn');

//  1 translate text
// add a click event listener to the translate button
translateButton.addEventListener('click', () => {
    // get the values from the input fields
    const sourceText = sourceTextarea.value;
    const sourceLang = sourceLanguageSelect.value;
    const targetLang = targetLanguageSelect.value;

    // if there's no text to translate, exit the function
    if (!sourceText) {
        return;
    }

    // to show a loading message while translating
    translatedTextarea.value = 'Translating...';

    // to make a POST request to our Flask backend API
    fetch('http://127.0.0.1:5000/translate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            text: sourceText,
            source_lang: sourceLang,
            target_lang: targetLang
        })
    })
    .then(response => response.json()) // Parse the JSON response
    .then(data => {
        // to display the translated text or an error message
        if (data.translated_text) {
            translatedTextarea.value = data.translated_text;
        } else if (data.error) {
            translatedTextarea.value = `Error: ${data.error}`;
        }
    })
    .catch(error => {
        // to handle network errors
        console.error('Error:', error);
        translatedTextarea.value = 'Error: Could not connect to the translation service.';
    });
});


// 2 optional feature: copy to clipboard 
copyButton.addEventListener('click', () => {
    const textToCopy = translatedTextarea.value;

    // to check if there is text to copy and it's not a message/error
    if (textToCopy && !textToCopy.startsWith('Error:') && !textToCopy.startsWith('Translating...')) {
        navigator.clipboard.writeText(textToCopy).then(() => {
            // to provide user feedback that the text was copied
            copyButton.textContent = 'Copied!';
            setTimeout(() => {
                copyButton.textContent = 'Copy';
            }, 2000); //  to reset button text after 2 seconds
        }).catch(err => {
            console.error('Failed to copy text: ', err);
        });
    }
});


// 3 optional feature: text-to-speech
speakButton.addEventListener('click', () => {
    const textToSpeak = translatedTextarea.value;
    const targetLang = targetLanguageSelect.value;
    
    // to check if there is text to speak and it's not a message/error
    if (textToSpeak && !textToSpeak.startsWith('Error:') && !textToSpeak.startsWith('Translating...')) {
        // to use the browser's built-in Web Speech API
        const utterance = new SpeechSynthesisUtterance(textToSpeak);
        utterance.lang = targetLang; // tp set the language for the speech
        
        window.speechSynthesis.speak(utterance);
    }
});