This script checks any web page's HTML for changes.

It looks at a specified section, compares it with the last saved version, and sends a macOS notification if something changed.

After each check, it saves the latest page HTML so it can compare again next time. 

Runs every 30 minutes via a launch agent. The website URL, heading title, and check interval can be set in `.env`. The plist file should also be updated before use.
