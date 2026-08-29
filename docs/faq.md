# FAQ

### Is it free?

Yes. MIT licensed, no sign-up, no limits beyond GitHub's API rate limits.

### Do I need a GitHub token?

No. A token only raises the rate limit when auditing many repositories in a row.

### Which repositories can it audit?

Any public repository. Private repositories need a token with `repo` scope.

### What does the score mean?

Each of the nine automated checks is worth one point (warnings count half). The
social preview is manual and not scored. 8+/10 means launch ready.

### Can I use it in CI?

Yes - `--strict` exits non-zero below 8/10, so a workflow fails when a
repository regresses.

### Is this affiliated with GitHub?

No. Independent tool, not affiliated with GitHub, Inc.

### Can I order updates to my delivery?

Yes - message us on Telegram mid-delivery and we adjust the pacing.
