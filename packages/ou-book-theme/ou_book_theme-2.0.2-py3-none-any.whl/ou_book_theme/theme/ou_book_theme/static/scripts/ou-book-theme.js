/**
 * Enable the toggle button on OU activities.
 */
function activitySetup() {
    for(const toggle of document.querySelectorAll('.ou-toggle')) {
        toggle.addEventListener('click', () => {
            toggle.classList.toggle('ou-toggle-hidden');
        });
    }
}

/**
 * Ensure all external links open in a new tab.
 */
function externalLinkSetup() {
    for (const externalLink of document.querySelectorAll('a.reference.external')) {
        externalLink.setAttribute('target', '_blank');
    }
}

function DOMContentLoaded() {
    activitySetup();
    externalLinkSetup();
}

document.addEventListener('DOMContentLoaded', DOMContentLoaded, false);
