// This script is injected directly into the <head> and runs immediately.

console.log("Hello from the test.js file! The script was successfully injected.");

// Add a robust event listener to the document.
// This ensures it works even with Gradio's dynamic UI updates.
document.addEventListener('click', function(e) {
    // Check if the clicked element is a button
    if (e.target.tagName.toLowerCase() === 'button') {
        alert("You clicked a button! (Event from injected JS)");
    }
});