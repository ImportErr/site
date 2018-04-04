# Discord integration specific settings.
# This does not involve statbot setup (see the DATABASES setting instead)
import os

# The guild ID to be used for permission checks.
DISCORD_GUILD_ID = 181866934353133570

# The webhook URL to send new events to.
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

# The role ID of the Administrator role.
DISCORD_ADMIN_ROLE_ID = 290546513656938496