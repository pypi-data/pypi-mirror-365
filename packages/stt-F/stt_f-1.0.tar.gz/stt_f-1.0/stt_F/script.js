const output = document.getElementById("output");
const startButton = document.getElementById("listenButton");
let isListening = false;

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();
recognition.lang = "en-IN";
recognition.interimResults = false;  // ⛔ Set to false = only final results
recognition.continuous = true;

startButton.addEventListener('click', () => {
    if (!isListening) {
        output.innerHTML = "<span style='color: gray;'>🕊️ Ruhani is capturing...</span>";
        recognition.start();
        startButton.textContent = '🎧 Ruhani is capturing...';
        isListening = true;
    }
});

recognition.addEventListener('result', (e) => {
    const transcript = e.results[e.resultIndex][0].transcript;

    output.innerHTML = `<span style='color: #6a0dad;'>🤍 Ruhani heard you:</span><br>${transcript}`;
});

recognition.addEventListener('end', () => {
    if (isListening) {
        recognition.start();
    }
});

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        recognition.stop();
        isListening = false;
        startButton.textContent = '🔊 Ruhani is Listening...';
        output.innerHTML += "<br><span style='color:red;'>⛔ Ruhani stopped listening (Escape pressed)</span>";
    }
});
