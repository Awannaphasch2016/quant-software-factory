import { z } from "zod";
import { discordCredentials } from "../discord-credentials.js";

/** Account numbers accepted from a Spec. */
export const ACCOUNT = /^[A-Za-z0-9-]{1,32}$/;

/** Dates accepted from a Spec. */
export const ISO_DATE = /^\d{4}-\d{2}-\d{2}$/;

/** The part of `checks.json` the tools read. */
export const checksSchema = z.array(z.object({ name: z.string(), passed: z.boolean() }).passthrough());

/** Resolves the bot token from the connector; it may be a value or a getter. */
export async function botToken(): Promise<string> {
  const token = discordCredentials.botToken;
  const value = typeof token === "function" ? await token() : token;
  if (!value) throw new Error("No Discord bot token is configured");
  return value;
}

/** The Discord channel id of the calling session, when it came from Discord. */
export function discordChannelId(channel: {
  kind: string;
  metadata: Readonly<Record<string, unknown>>;
}): string | null {
  const id = channel.metadata.channelId;
  return channel.kind.endsWith("discord") && typeof id === "string" ? id : null;
}
