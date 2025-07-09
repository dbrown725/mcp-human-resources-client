let recentInputs = [];
const maxRecentInputs = 15; // Maximum number of recent inputs to store
const textarea = document.getElementById('myInput');
const recentInputsSelect = document.getElementById('recent-inputs');

// Load from localStorage
{
  const stored = localStorage.getItem('recentInputs');
  if (stored) {
    try {
      recentInputs = JSON.parse(stored);
    } catch (e) {}
  }
}

// Update recent inputs list
function updateRecentInputs(value) {
  // Check if the input text is not empty and not already in the list
  if (value.trim() !== '' && !recentInputs.includes(value)) {
    recentInputs.push(value);
    recentInputs = recentInputs.slice(-maxRecentInputs); // Limit the list to maxRecentInputs
    localStorage.setItem('recentInputs', JSON.stringify(recentInputs));
    populateRecentInputsDiv();
  }
}

// Populate recent inputs div
function populateRecentInputsDiv() {
  const recentInputsDiv = document.getElementById('recent-inputs');
  recentInputsDiv.innerHTML = '';
  recentInputs.forEach((input, index) => {
    const recentInputDiv = document.createElement('div');
    recentInputDiv.textContent = input;
    recentInputDiv.className = `recent-input ${index % 2 === 0 ? 'grey-bg' : 'white-bg'}`;
    recentInputDiv.addEventListener('click', () => {
      textarea.value = input;
      textarea.style.height = '';
      textarea.style.height = textarea.scrollHeight + 'px';
      modal.style.display = "none";
    });
    recentInputsDiv.appendChild(recentInputDiv);
  });
  recentInputsDiv.style.display = recentInputs.length > 0 ? 'block' : 'none';
}

function styleParagraphs() {
    // Select all paragraphs within the div with id "output"
    const paragraphs = document.querySelectorAll('#output p');

    // Filter paragraphs that start with "System prompt" or "Your input:"
    paragraphs.forEach((paragraph) => {
        const text = paragraph.innerHTML.trim();
        if (text.startsWith('System prompt') || text.startsWith('Your input:')) {
            // Change the background color of the matching paragraphs to white
            paragraph.className = 'prompt';
        } else if (text.startsWith('Error:')) {
            // Change the background color of the matching paragraphs to light red
            paragraph.className = 'error';
        }
    });
}

const outputDiv = document.getElementById('output');
const toolsDiv = document.getElementById('toolsInUse');
const spinner = document.getElementById('spinner');
let inputSubmitted = true;
//For the initial page load
spinner.classList.add('loader');

function sendUserInput() {
    spinner.classList.add('loader');
    inputSubmitted = true;
    let userInput = textarea.value;

    updateRecentInputs(userInput);

    // Replace newlines with spaces
    userInput = userInput.replace(/[\r\n]+/g, ' ');
    textarea.value = '';
    userInput = userInput.trim();
    eel.send_input(userInput);
}

textarea.addEventListener('keypress', function (event) {
    if (event.key === 'Enter') {
        sendUserInput();
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const arrowIcon = document.querySelector('.arrow-icon');
    arrowIcon.addEventListener('click', function () {
        sendUserInput();
    });
});

const newChatButton = document.getElementById('newChatButton');
newChatButton.addEventListener('click', function () {
    outputDiv.innerHTML = "";
    textarea.value = "";
    textarea.style.height = '60px';
    eel.send_input("NEW_CHAT");
});

const renderer = {
    link(href, title, text) {
      const link = marked.Renderer.prototype.link.call(this, href, title, text);
      return link.replace('<a', '<a target="_blank" rel="noopener noreferrer"');
    }
  };
  
marked.use({ renderer });

// Get the modal
var modal = document.getElementById("myModal");

// Get the button that opens the modal
var btn = document.getElementById("recentSearchesButton");

// Get the <span> element that closes the modal
var recentSpan = document.getElementsByClassName("recent-close")[0];

// When the user clicks on the button, open the modal
btn.onclick = function() {
  modal.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
recentSpan.onclick = function() {
  modal.style.display = "none";
}

// Get the button that opens the tools modal
var toolsButton = document.getElementById("toolsInUseButton");

// Get the <span> element that closes the tools modal
var toolsCloseSpan = document.querySelector('#toolsModal .tools-close');

// When the user clicks on the button, open the tools modal
toolsButton.onclick = function() {
  toolsModal.style.display = "block";
}

// When the user clicks on <span> (x), close the tools modal
toolsCloseSpan.onclick = function() {
  toolsModal.style.display = "none";
}

// When the user clicks anywhere outside of the tools modal, close it
window.onclick = function(event) {
  if (event.target == toolsModal) {
    toolsModal.style.display = "none";
  }
  if (event.target == modal) {
    modal.style.display = "none";
  }
}

window.addEventListener('load', populateRecentInputsDiv);

let firstOutputComplete = false;
let timeoutStarted = false;

eel.expose(displayOutput);
function displayOutput(output) {
  if(inputSubmitted === true) {
    inputSubmitted = false;
  } else {
    spinner.classList.remove('loader');
  }
  let parsedMarkdown = marked.parse(output);

  if (timeoutStarted === false) {
    setTimeout(() => {
        firstOutputComplete = true;
    }, 2000);
    timeoutStarted = true;
  }

  if (firstOutputComplete === false) {
    toolsDiv.innerHTML += parsedMarkdown;
    toolsModal.style.display = "none";
    return;
  }
  if (!output.includes("NEW_CHAT")) {
    outputDiv.innerHTML += parsedMarkdown;
    styleParagraphs();
  }
  outputDiv.scrollTop = outputDiv.scrollHeight; // Scroll to the bottom
}

// Start the Python subprocess when the page loads
eel.start_process();
