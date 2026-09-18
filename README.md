<div align="center">
  <img src="docs/action-bandit-plain-logo.png" alt="Bandit Reviewdog Action Logo" style="width: 30%; height: 30%;">
  <h1>action-bandit</h1>
</div>


<h3 align="center" style="margin-top: 0; font-weight: 400;">
  A GitHub Action that runs <a href="https://github.com/PyCQA/bandit" target="_blank" rel="noopener noreferrer">Bandit</a> — a security linter for Python — and reports issues directly on pull requests using <a href="https://github.com/reviewdog/reviewdog" target="_blank" rel="noopener noreferrer">reviewdog</a>.
</h3>

<div align="center" style="font-style: italic">
  Designed for automated, inline security feedback during code review, combining Bandit's static analysis with reviewdog's flexible reporting workflows.
</div>

<br>

<p align="center">
  <a href="#"><img src="https://img.shields.io/github/v/release/brunohaf/action-bandit?logo=github&sort=semver" alt="Latest Release"></a>
  <a href="#"><img src="https://github.com/brunohaf/action-bandit/workflows/Test/badge.svg" alt="Test Workflow"></a>
  <a href="#"><img src="https://github.com/brunohaf/action-bandit/workflows/reviewdog/badge.svg" alt="reviewdog Workflow"></a>
  <a href="#"><img src="https://github.com/brunohaf/action-bandit/workflows/depup/badge.svg" alt="depup Workflow"></a>
  <a href="#"><img src="https://github.com/brunohaf/action-bandit/workflows/release/badge.svg" alt="release Workflow"></a>
  <a href="https://github.com/haya14busa/action-bumpr"><img src="https://img.shields.io/badge/bumpr-supported-ff69b4?logo=github" alt="action-bumpr supported"></a>
</p>

<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#usage">Usage</a> •
  <a href="#related">Related</a> •
  <a href="#credits">Credits</a> •
  <a href="#license">License</a>
</p>

## Key Features

* **Automated Python Security Scanning** — Uses [Bandit](https://github.com/PyCQA/bandit) to statically analyze Python code and detect common security issues before they reach production.
* **Actionable Feedback in Pull Requests** — Surfaces issues early in the review process, allowing developers to address them before merging. Frees human reviewers to focus on architecture and complex logic—not repetitive static checks.
* **Flexible Reporting with [reviewdog](https://github.com/reviewdog/reviewdog)** — Choose how results are reported to fit your workflow:

  * **Inline PR Comments** — Adds comments directly to affected lines for contextual feedback.
  * **GitHub Checks** — Pair with required [Github Checks](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/about-status-checks#checks) to enforce security gates on pull requests. .
  * **Commit Status + Checks** — Reports as both [commit statuses and GitHub Checks](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/about-status-checks#types-of-status-checks-on-github) for complete CI feedback.
* **Targeted Analysis with Filtering** — Analyze only changed files in PRs using `filter_mode`, reducing noise and improving relevance.
* **Configurable** — Supports `pyproject.toml` or Bandit configuration files for analysis settings, and [reviewdog’s options](https://github.com/reviewdog/reviewdog?tab=readme-ov-file) for tuning output and behavior.
* **Debugging and Troubleshooting** — Enable `verbose: true` for detailed logs and use [reviewdog’s debugging flags](https://github.com/reviewdog/reviewdog?tab=readme-ov-file#debugging) for in-depth diagnostics.

<br>

---

> *This action [installs and runs reviewdog locally](https://github.com/reviewdog/reviewdog?tab=readme-ov-file#option-2-install-reviewdog-github-apps) in the GitHub Actions runner using `GITHUB_TOKEN` for authentication. All analysis and reporting happens within the runner. For stronger isolation and control, use self-hosted runners.*

---
<br>

## Usage

### Inputs

| Input             | Description                                                           | Default               |
| ----------------- | --------------------------------------------------------------------- | --------------------- |
| `github_token`    | GitHub Token for API access                                           | `${{ github.token }}` |
| `workdir`         | Directory relative to root to run Bandit                              | `.`                   |
| `bandit_config`   | Path to Bandit configuration file                                     | `""`                  |
| `bandit_flags`    | Extra Bandit CLI flags                                                | `""`                  |
| `verbose`         | Enable verbose logging                                                | `false`               |
| `summary`         | Write a findings report to the GitHub job summary                     | `false`               |
| `tool_name`       | Tool name used in reviewdog output                                    | `bandit`              |
| `level`           | Report level (`info`, `warning`, `error`)                             | `error`               |
| `reporter`        | Reporter type (`github-check`, `github-pr-review`, `github-pr-check`) | `github-check`        |
| `filter_mode`     | Filtering mode (`added`, `diff_context`, `file`, `nofilter`)          | `added`               |
| `fail_level`      | Fail when an issue at or above this level is found (`none`, `any`, `info`, `warning`, `error`) | `""` (never fails) |
| `fail_on_error`   | **Deprecated** — use `fail_level`. Whether to fail the build when errors are found | `false`               |
| `reviewdog_flags` | Additional flags for reviewdog                                        | `""`                  |

Bandit severities reach reviewdog as `HIGH` → `error`, `MEDIUM` → `warning`,
`LOW` → `info`, so `fail_level: error` fails only on high-severity findings.

`fail_on_error` meant a different threshold depending on `reporter` — any
finding for `github-pr-review`, error-level only for `github-check` and
`github-pr-check`. It still maps to that same threshold, and warns. `fail_level`
means the same thing whatever the reporter.

### Configuration Example

```yaml
name: Run Bandit
on: [pull_request]

jobs:
  bandit:
    name: Bandit Security Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: brunohaf/action-bandit@v1
        with:
          github_token: ${{ secrets.github_token }}
          reporter: github-pr-review
          level: warning
```

<br>

> *Refer to the [this workflow](https://github.com/brunohaf/action-bandit/blob/main/.github/workflows/test.yml) for more usage examples.*

### Job Summary

Setting `summary: true` appends a findings report to the
[job summary](https://docs.github.com/actions/reference/workflows-and-actions/workflow-commands#adding-a-job-summary)
of the run:

```yaml
      - uses: brunohaf/action-bandit@v1
        with:
          summary: true
```

Reviewdog only annotates code that the pull request touched, as set by
`filter_mode`. The job summary is built from the full Bandit report instead, so
it also covers findings in files the pull request did not change.

### Screenshots

**PR Review (github-pr-review)**  
<div>
  <img src="https://user-images.githubusercontent.com/3797062/73162963-4b8e2b00-4132-11ea-9a3f-f9c6f624c79f.png" alt="PR Review Example" width="600"/><br>
</div>
<br>

**Check Run (github-check)**  
<div>
  <img src="https://user-images.githubusercontent.com/3797062/73163032-70829e00-4132-11ea-8481-f213a37db354.png" alt="Check Example" width="600"/>
</div>
<br>

> *Source: <a href="https://github.com/reviewdog/action-composite-template/blob/main/README.md">reviewdog/action-composite-template</a>*

## Related

* [reviewdog](https://github.com/reviewdog/reviewdog) — Integrates linter results with GitHub code reviews.
* [Bandit](https://github.com/PyCQA/bandit) — Python static security analyzer by PyCQA.
* [Public reviewdog GitHub Actions](https://github.com/reviewdog/reviewdog?tab=readme-ov-file#public-reviewdog-github-actions) — List of related GitHub Actions.
* [Bandit GitHub Action by PyCQA](https://github.com/PyCQA/bandit-action) — The official GitHub Action for running Bandit, maintained by PyCQA.

## Credits


* Bootstrapped with [reviewdog/action-composite-template](https://github.com/reviewdog/action-composite-template).
* Based on [reviewdog/action-eslint](https://github.com/reviewdog/action-eslint), with additional inspiration from [jordemort/action-pyright](https://github.com/jordemort/action-pyright).

## License

[MIT](LICENSE)
