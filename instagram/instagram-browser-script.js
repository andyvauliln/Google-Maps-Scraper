// A set to hold the unique post IDs.
const postIDs = new Set();

// Create a function to extract post IDs from the page.
function extractPostIDs() {
    // Get all the post link elements on the page.
    const elements = document.querySelectorAll('a[href^="/p/"]');

    // Add each post ID to the set.
    for (const element of elements) {
        // Extract post ID from the href attribute
        const postId = element.getAttribute('href').split('/')[2];
        postIDs.add(postId);
        console.log(postIDs)
    }
}

// Create a MutationObserver to watch for changes to the page.
const observer = new MutationObserver((mutationsList, observer) => {
    for (let mutation of mutationsList) {
        // If the mutation is a childList mutation and addedNodes isn't empty, extract post IDs.
        if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
            extractPostIDs();
        }
    }
});

// Start observing the document with the configured parameters.
observer.observe(document, { childList: true, subtree: true });

// You can now scroll the page, and post IDs will be collected as new posts load in.

// When you're done, you can stop the observer and log the post IDs.
observer.disconnect();
console.log(Array.from(postIDs));