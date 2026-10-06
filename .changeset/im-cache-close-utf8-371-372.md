---
"mrbinnacle-skills": patch
---

`im-down` and `im-up`: the close now shares the receiver-check cache, and check output no longer crashes the validator on Windows (#371, #372).

What changes for you if you have these cards installed:

- **The close and the open share one cache.** `close_session.py` now runs your receiver checks through the same runner and cache as the open. A check that declares `cache_inputs` and passes at the close is reported `cached` at the next `/im-up` on an unchanged tree, so it no longer runs twice across one session boundary. The packet's `tests[]` entries gain a `status` field. The weekly uncached audit can now fall on a close as well as an open; a disagreement refuses that close.
- **The docs state the real cache key.** The key is a sha256 over the command string, the Python version, `git --version`, and the sha256 of each input file's bytes on disk with its path. These are working files, not git blobs: an uncommitted edit changes the key, and a directory input covers untracked and ignored files under it. The previous docs said "blob hashes"; the behaviour has not changed.
- **Cache writes are atomic.** Each write goes to a temp file and is renamed into place, so an interrupted write or two sessions writing at once cannot leave a corrupt cache file.
- **A relative `receiver_check_cache` path resolves under `~/.cache/mrbinnacle-skills/`**, never inside your repository. Before, it resolved against the repository root. A relative path that climbs out of that directory with `..` is refused. Absolute and `~` paths behave as before. If you set a relative path, your cache moves and the first session after upgrading runs every check once.
- **Check output and git output decode as UTF-8 with replacement**, whatever your locale. On a Windows host with a cp1252 locale, a receiver check that printed a character outside cp1252 crashed the validator, and so could a branch name containing such a character. Both now report normally. The same holds for `close_session.py` and for `snapshot_state.py`, the lower-level close path, which crashed the same way on such output.
- **The cache key no longer depends on how the repository root is spelled.** Each input's path enters the key resolved, so a Windows 8.3 short name and its long form, or a path with a `..` segment, key the same and the cache hits.
- **A check served from the cache is labelled in the packet.** Its `tests[]` entry carries `cache_key` and `cached_at`, and its `observed_at` is the time of the cached run, not of the close.
