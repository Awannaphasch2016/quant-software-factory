import { discordChannel } from "eve/channels/discord";
import { discordCredentials } from "../discord-credentials.js";

export default discordChannel({ credentials: discordCredentials });
