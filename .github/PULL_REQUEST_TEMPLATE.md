**Description:** Describe in a couple of sentence what this PR adds

**JIRA:** Link to JIRA ticket

**Dependencies:** dependencies on other outstanding PRs, issues, etc. 

**Merge deadline:** List merge deadline (if any)

**Installation instructions:** List any non-trivial installation 
instructions.

**Testing instructions:**

1. Open page A
2. Do thing B
3. Expect C to happen
4. If D happened instead - check failed.

**Reviewers:**
- [ ] tag reviewer 
- [ ] tag reviewer 

**Merge checklist:**
- [ ] All reviewers approved
- [ ] CI build is green
- [ ] Commit messages (and PR title, if squash merging) use the correct
      [Conventional Commits](https://docs.openedx.org/projects/openedx-proposals/en/latest/best-practices/oep-0051-bp-conventional-commits.html#specification) type — they determine the
      release: `fix:` → patch, `feat:` → minor, `!` / `BREAKING CHANGE:` → major
- [ ] Documentation updated (not only docstrings)
- [ ] Commits are squashed

**Post merge:**
- [ ] Check new version is pushed to PyPI after the release workflow is
      finished.
- [ ] Delete working branch (if not needed anymore)

**Author concerns:** List any concerns about this PR - inelegant 
solutions, hacks, quick-and-dirty implementations, concerns about 
migrations, etc.
