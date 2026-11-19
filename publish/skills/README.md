# ukwhatn/skills

Claude Code plugins that carry the development workflow I use every day: skills for writing, coding, debugging, screen design and review, and optional hooks that make Claude invoke them.

The skills are written in Japanese. They also handle English text (`writing-prose` covers English messages and calls `humanizer`), but the instructions themselves are Japanese.

[日本語](README.ja.md)

## Plugins

### ukwhatn-skills

- `dev-flow`: how to work. Check primary sources before stating facts, look for existing code before writing new code, ask before outward actions (push, posting), and follow a plan-to-report flow for larger tasks. The other skills refer to its sections.
- `writing-prose`: messages, PR descriptions, review comments, documents and emails that a reader understands on the first read. For Japanese it runs a register checker and `yomiyasu`; for English it runs `humanizer`.
- `writing-code`: follow existing patterns, design deep modules, test at seams, keep comments to what code and tests can't say.
- `systematic-debugging`: find the root cause before changing code, when the first fix didn't work.
- `writing-ui-text`: Japanese UI text (buttons, headings, errors, empty states).
- `designing-ui`: choose navigation, overlay, feedback and layout patterns from decision tables and keep them consistent across screens.
- `self-review`: check your own branch's diff before opening a PR.
- `pr-review`: review a pull request with Claude Code and an external CLI (Codex by default).
- `grilling`: question a plan or design to surface assumptions and open decisions.
- `yomiyasu` and `humanizer`: unmodified copies of [nanaism/yomiyasu](https://github.com/nanaism/yomiyasu) and [blader/humanizer](https://github.com/blader/humanizer), used by `writing-prose`.

Skills load only when they are invoked, so the rules in `dev-flow` don't apply to every turn the way a `CLAUDE.md` does. Copy the parts you want always on into your own `CLAUDE.md`.

### ukwhatn-guards (disabled by default)

- A hook that blocks code edits until `writing-code` has been invoked, and outward posts (Slack, GitHub comments, email drafts) until `writing-prose` has been invoked.
- A hook that checks outgoing Japanese text for spoken-style verbs and tables that don't fit the rules, and asks once for a rewrite.
- The `ukwhatn-style` output style (Japanese). It takes effect only after you select it in `/config`.

These hooks stop tool calls in your sessions, so the plugin stays off after you install it. Enable it if you want the skills enforced.

## Install

```sh
claude plugin marketplace add ukwhatn/skills
claude plugin install ukwhatn-skills@ukwhatn
```

To add the guards:

```sh
claude plugin install ukwhatn-guards@ukwhatn
claude plugin enable ukwhatn-guards@ukwhatn
```

`ukwhatn-guards` depends on `ukwhatn-skills` and installs it if needed.

## Optional skills

`designing-ui` uses these skills when they are installed and skips those steps when they aren't. Install them from upstream if you want them:

- [heydamir/unslop](https://github.com/heydamir/unslop): visual polish for new screens
- [shadcn-ui/ui](https://github.com/shadcn-ui/ui) (`skills/shadcn`): shadcn/ui component APIs
- [GoogleChrome/modern-web-guidance](https://github.com/GoogleChrome/modern-web-guidance): how to build a chosen pattern with current web platform features

## How this repository is maintained

The source lives in my own Claude Code configuration. A script copies the published skills here, removes the parts that only apply to my setup, and rewrites the references between skills. The version goes up whenever the exported content changes.

Issues and pull requests are welcome. I apply accepted changes to the source and export again, so your change arrives in a later export commit.

## License

MIT for the original work (`LICENSE`). The adapted works, the bundled copies and their licenses are listed in [NOTICE.md](NOTICE.md).
