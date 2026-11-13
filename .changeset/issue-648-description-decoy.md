---
"mrbinnacle-skills": patch
---

The card-file check reads a card's description more strictly in three places (#648). It refuses a frontmatter with more than one line that starts with `description:`. Before this change it measured the first such line, so a short decoy inside a multi-line `license:` value, or a duplicate key, let a 300-character description pass the 200-character bar. It now reads a one-word value that starts with a digit, such as `3d-printing` or `1st`, as text, and refuses only what YAML 1.1 or 1.2 reads as a number or date. Before this change those values were refused with a message that the card states no description. It refuses a description that holds nothing but escapes and spaces, such as `"\0"` or `"  "`. Every published card already passes, so no card changes and an installed user loses nothing.
