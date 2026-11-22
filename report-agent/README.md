# report-agent

A single [eve](https://www.npmjs.com/package/eve) agent that turns a Report
Spec sent in Discord into the Returns & Transactions report. The Python report
code in this repository computes and checks every figure; the model only reads
the Spec and calls tools.

Mock data only. Live data goes through `private_run` in the trusted zone; see
Software Design section 2.9 in [`../docs/4-software-design.md`](../docs/4-software-design.md).

## How a request flows

1. Someone runs `/ask` in Discord with the Spec as text or as an attached file.
2. The model reads the Spec (`read_spec_file` for an attachment) and calls
   `generate_report` with the dataset, account, opening date and as-of date.
3. `generate_report` runs `quant_software_factory.reporting.returns_transactions`
   in a Vercel Sandbox, from a checkout pinned at `REPO_REF` in
   [`agent/sandbox.ts`](agent/sandbox.ts). The sandbox has no network access.
4. If every check passes, the tool posts the report to the Discord channel
   itself: a summary line with `report.md` attached, then the report text with
   tables in code blocks. The model gets only the status and the check names.
5. The model replies with one line. On a failure it names the failed checks.

## Layout

| Path | What it does |
| --- | --- |
| `agent/agent.ts` | Model, no built-in tools (`defaultTools: false`), session usage cap |
| `agent/instructions.md` | System prompt: read the Spec, call the tool once, never write figures |
| `agent/sandbox.ts` | Vercel Sandbox: clones this repo at `REPO_REF` at build time, runs with network denied |
| `agent/tools/generate_report.ts` | Runs the report, posts it to Discord, hides it from the model |
| `agent/tools/read_spec_file.ts` | Reads text files attached in chat, and nothing else |
| `agent/lib/discord-report.ts` | Table formatting and the Discord REST calls for posting a report |
| `agent/discord-credentials.ts` | Bot credentials from the Vercel Connect connector `discord/qsf-report-agent` |
| `agent/channels/discord.ts` | Discord channel, slash command mode |
| `agent/channels/eve.ts` | eve's own channel, for the dev TUI and `eve remote` |
| `test/` | Tests for `agent/lib/` (Node test runner) |

## Commands

Node 26 and pnpm (version in `package.json`).

```bash
pnpm install
pnpm typecheck        # tsc
pnpm test             # node --test on test/**/*.test.ts
pnpm dev              # local eve dev server (needs Docker for the sandbox)
```

Deploy to the Vercel project (team owner's approval first, since runs are
billed to the team):

```bash
vercel deploy --prod --scope <team>
```

The report code is pinned: after changing it, update `REPO_REF` to a commit on
`main` and redeploy.

## Discord setup

Done once per bot. The setup asks for the bot token in the terminal; never
commit it.

```bash
npx eve add channel/discord --skip-install          # first time
npx eve add channel/discord --skip-install --overwrite   # to change it later
```

Choose "A slash command". The setup creates the Vercel Connect connector,
registers `/ask` and points Discord's Interactions Endpoint at Vercel. Invite
the bot with the link it prints. Posting the report needs the Send Messages
and Attach Files permissions in the channel.

## Known limits

- One report type and one mock dataset (`demo_coop_rg_2026_10_v2`).
- The agent reads only dataset, account and dates from the Spec. Other Spec
  sections (blocks, writing rules, language) are not applied.
- Anyone in a server that has the bot can run `/ask`.
