import { localDev, vercelOidc } from "eve/channels/auth";
import { eveChannel } from "eve/channels/eve";

/**
 * eve's own channel, for the dev TUI and for testing the deployed agent with
 * a Vercel OIDC token before Discord is connected.
 */
export default eveChannel({ auth: [localDev(), vercelOidc()] });
