import { posix } from "node:path";
import { defineTool } from "eve/tools";
import { z } from "zod";
import { environment } from "../sandbox.js";

/** eve stores chat attachments under this sandbox folder. */
const ATTACHMENTS_DIR = ".eve/attachments";

/** A Spec is a short text file; anything larger is not a Spec. */
const MAX_CHARS = 50_000;

const outputSchema = z.object({
  content: z.string().nullable(),
  error: z.string().nullable(),
});

/**
 * Reads a Spec file that someone attached in chat.
 *
 * @remarks
 * The agent has no built-in file tools (`defaultTools: false`), so without
 * this tool an attached Spec is only a path the model cannot open. The tool
 * reads text files inside eve's attachment folder and nothing else, so it
 * cannot be used to read the report code, fixtures or other sandbox files.
 */
export default defineTool({
  description:
    "Read a Spec file attached to the message. Pass the path from the 'Attached file <path>' note exactly as shown. Only attached text files can be read.",
  inputSchema: z.object({
    path: z
      .string()
      .min(1)
      .max(512)
      .describe("Path from the 'Attached file <path> (<type>)' note"),
  }),
  label: {
    complete: (_input, output) =>
      output.error === null ? "Read the attached Spec" : "Could not read the attached file",
    start: () => "Reading the attached Spec",
  },
  outputSchema,
  async execute(input, ctx) {
    const sandbox = await ctx.getSandbox(environment);
    const root = posix.normalize(sandbox.resolvePath(ATTACHMENTS_DIR));
    const target = posix.normalize(
      posix.isAbsolute(input.path) ? input.path : sandbox.resolvePath(input.path)
    );
    if (!target.startsWith(`${root}/`)) {
      return { content: null, error: "Only files attached to the message can be read." };
    }

    const text = await sandbox.readTextFile({ path: target });
    if (text === null) {
      return { content: null, error: "The attached file was not found." };
    }
    if (text.includes("\u0000")) {
      return { content: null, error: "The attached file is not a text file." };
    }
    if (text.length > MAX_CHARS) {
      return {
        content: null,
        error: `The attached file is over ${MAX_CHARS} characters, too long for a Spec.`,
      };
    }
    return { content: text, error: null };
  },
});
