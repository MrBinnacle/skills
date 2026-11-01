---
"mrbinnacle-skills": patch
---

The verification gate in `mechanisms/verify-gate` now tracks a written file inside the project when the project root and the file path spell the same directory differently. On Windows one directory has a long name and an 8.3 short name, such as `C:\Users\runneradmin` and `C:\Users\RUNNER~1`. `underRoot` compared the two spellings as text, returned false, and the gate stayed silent when it should have asked for a check. It now also compares the real spelling of each path, from `realpathSync.native`. A file that does not exist yet is compared through its nearest existing parent. The text comparison stays, so a symlink inside the project that points outside it is still tracked. The plugin manifests do not ship `mechanisms/`, so installed users get nothing new.
