import { defineAgent } from "eve";

/**
 * The single report agent.
 *
 * @remarks
 * One agent, no subagents. It reads a Report Spec, calls `generate_report`,
 * and replies with the report the code produced. The model never computes
 * or edits a figure; the Python report code in the sandbox does. Model ids
 * are Vercel AI Gateway strings, matching the factory template's choice.
 */
export default defineAgent({
  // No bash, file or web tools: the only way to produce a report is
  // `generate_report`, so the model cannot compute figures in the sandbox.
  defaultTools: false,
  limits: {
    // One report needs one tool call and a short reply. Stop a session that
    // runs far past that instead of spending the team's budget.
    sessionUsage: ({ window }) =>
      window.outputTokens >= 20_000 || (window.costUsd ?? 0) >= 2,
  },
  model: "anthropic/claude-opus-5.5",
});
