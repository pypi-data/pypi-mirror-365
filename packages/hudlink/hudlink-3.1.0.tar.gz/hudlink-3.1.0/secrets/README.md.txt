# IPUMS API Token

This directory stores your IPUMS API token required to access the IPUMS data retrieval functionality in HUDLink.

## Getting an IPUMS API Token
1. Visit the IPUMS website: https://api.ipums.org/
2. Log in or create an account.
3. Navigate to your **API Access** page and generate a new API token.

## Installing Your Token
1. Open the file `ipums_token` in this directory.
2. Replace the placeholder text:
YOUR_TOKEN_HERE

with your actual API token. **Do not** include quotation marks or extra whitespace.
3. Save the file. HUDLink will read this token at runtime to authenticate API requests.

---

> **Important:** Keep this file secret and never commit it to public repositories.