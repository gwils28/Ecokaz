#!/usr/bin/env bash
# PreToolUse (Bash): sole-contributor policy and no git hook bypass.
# Only git invocations are inspected, so docs that mention these words can still be edited.
set -euo pipefail
cmd=$(jq -r '.tool_input.command // empty')
grep -qE '(^|[;&|(]|\s)git\s' <<<"$cmd" || exit 0
# hooksPath: block setting or unsetting it, not reading it (`git config core.hooksPath`).
hooks_write='git\s+config\s+(--\S+\s+)*core\.hooksPath\s+[^;&|[:space:]]|git\s+config\s.*--unset(-all)?\s+core\.hooksPath'
if grep -qiE "git\s.*(co-authored-by|--no-verify)|$hooks_write" <<<"$cmd"; then
  echo "Blocked: co-author trailers, --no-verify and hooksPath changes are not allowed. The maintainer commits." >&2
  exit 2
fi
exit 0
