[latest updates at the bottom]

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


---

UI Idea 2:
the layout to implement:

under the section, create a div that has side scrolling 
it will hold cards that scroll sideways.
one card already exists in the code. the card that has the input and results display. 
get every QnA and create a card for it; card header has the Qn, card footer has the response
cards move from left to right in order of oldest to newest.

for the input card [will be the default card seen and focussed on]
the input will be at the top as I've edited it in the html.
then the response will be at the bottom, in the card body.

---

UI Idea 2:
the layout to implement:

cards still remain intact
change the inference card thus:
in the body section, 
- move the form for the prompt input to come just below
- then the horizontal scrollable section of results cards as before
- every time a prompt is sent, a card is created with its response. 
- that latest card should always be in focus on first / subsequent page loads
- whenever a new qna is added tot he scroll list, let it be the focus.