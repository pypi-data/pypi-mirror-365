# Developer Documentation

This area of the documentation contains information for developers of the OU Book Theme.

## Updating the OU headers and footers

To update the OU headers / footers follow these steps:

1. Replace the content of {file}`ou_book_theme/theme/ou_book_theme/ouheaders` with the newest versions of the {file}`gui`
   and {file}`js` folders from the updated theme. Then:

   1. In the {file}`ou_book_theme/theme/ou_book_theme/ouheaders/gui/headerfooter.min.css` replace all occurrences of
      `/ouheaders/gui` with `.`.
   2. In the {file}`ou_book_theme/theme/ou_book_theme/ouheaders/js/src/ou-header.js` replace all occurrences of
      `'/ouheaders` with `document.querySelector('html').getAttribute('data-content_root') + 'ouheaders`.
   3. Run {guilabel}`hatch run build-ou-branding` to build the minified version

2. Replace the contents of the {file}`ou_book_theme/theme/ou_book_theme/ou-header.html` with the content from the updated
   theme. Then:

   1. In the updated file replace all occurrences of `/ouheaders` with `{{ content_root }}ouheaders`
   2. In the updated file comment out the Google Tag Manager tracking iframe
   3. In the updated file comment out the Skip-to-main-content link

3. Replace the contents of the {file}`ou_book_theme/theme/ou_book_theme/ou-footer.html` with the content from the updated
   theme. Then:

   1. In the updated file replace all occurrences of `/ouheaders` with `{{ content_root }}ouheaders`

4. Replace the contents of the {file}`ou_book_theme/theme/ou_book_theme/ou-head.html` with the content from the updated
   theme. Then:

   1. In the updated file replace all occurrences of `/ouheaders` with `{{ content_root }}ouheaders`
