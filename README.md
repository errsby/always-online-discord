# Discord Selfbot + Cloudflare Worker API

This will not run off cloudflare workers, you will need a server for the selfbot in addition to the worker. The selfbot sends about ~1,500 worker requests a day.


## Functionality

- Show rotating status messages (e.g. quotes, moods, activities)
- Control DND behavior and schedule it based on time
- Update your status remotely through a hosted API
- Manage multiple users/accounts with unique configs

### Selfbot (bot.js)

- Custom status control: Static or rotating text
- Pulls all config remotely from API every 60 seconds
- Respects DND time windows with separate status message

### Cloudflare Worker API (worker.js)

- Lightweight, fast, serverless JSON API
- Unique config per user (`/username` routes)
- Extendable to support more users or linked storage
