---
"mrbinnacle-skills": patch
---

A top-level `mechanisms/` directory now sits beside the cards. It holds four Pi extensions, each named in `mechanisms/README.md` with the card it enforces and the harness event it fires on: a verification gate, an end-of-line guard, an in-process reviewer and a session packet. Two of them enforce candidates that are not admitted (`uniform-eol` and `reviewer-horizon`), and the README says so. No card is added, and the plugin manifests do not ship `mechanisms/`, so installed users get nothing new. `im-down` and `im-up` `PACKET-FORMAT.md` document two optional manifest keys, `previous_packet_id` and `parked`. The card scripts neither write nor check them, so a packet without them is still complete.
