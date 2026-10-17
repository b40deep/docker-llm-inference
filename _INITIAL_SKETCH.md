# for the pw page

---
text: tekamu password
input: pw input [focus defaults here so i can type as soon as the page loads]
btn: yingila
---

# for the main inference page

- overall entire page must not have scroll at all. all elements must fit within the vertical space and have individual scroll bars where needed.
- proportions given are out of 20 e.g., navbar: 1/20

---
navbar: 1/20
    - left
        - app name: chapatiGPT
    - right
        - checkbox: use past responses
        - pill: inference status
        - btn: logout
main content:
    - row 1/20
        - small label: previous results
        - btn: clear results
    - row remainder/20
        - [display prev results here]
        - don't autospace. keep same space whether 2 results or 200.
        - use scrollbar when needed.
    - row 2/20, expanding to 10 max
        - text input for the prompt: [same placeholder as current]

