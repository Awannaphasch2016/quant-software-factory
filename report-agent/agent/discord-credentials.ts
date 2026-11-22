import { connectDiscordCredentials } from "@vercel/connect/eve";

/**
 * Discord bot credentials from the Vercel Connect connector.
 *
 * @remarks
 * Shared by the Discord channel and by `generate_report`, which posts the
 * report itself so the model never sees it. No token is stored in the repo.
 */
export const discordCredentials = connectDiscordCredentials("discord/qsf-report-agent");
