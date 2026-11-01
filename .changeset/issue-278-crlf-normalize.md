---
"mrbinnacle-skills": patch
---

Line endings only. Nineteen tracked text files held CRLF in the git index: seventeen whole files and two `test_validate_packet.py` files with mixed endings. Each is now LF, with no change to content. `.gitattributes` now pins the whole repository with `* text=auto eol=lf`. It drops the comment that explained why it did not. One file stays CRLF on purpose: `site/fonts/LICENSE.txt`, IBM's licence, copied byte for byte from the font package.
