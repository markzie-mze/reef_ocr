# Anthropic API Setup Guide

This guide covers how to get and configure your Anthropic API key for datasheet extraction.

## Getting an API Key

### 1. Create an Anthropic Account

1. Go to [console.anthropic.com](https://console.anthropic.com/)
2. Sign up with your email
3. Verify your email address

### 2. Set Up Billing

The API requires a payment method:

1. Go to **Settings** → **Billing**
2. Add a credit card
3. Set a spending limit (recommended: start with $10-20)

### 3. Create an API Key

1. Go to **Settings** → **API Keys**
2. Click **Create Key**
3. Name it (e.g., "SHAMS Datasheet Extraction")
4. Copy the key immediately - you won't see it again!

The key looks like: `sk-ant-api03-xxxxx...xxxxx`

## Setting the API Key

### Option 1: Environment Variable (Recommended)

**Mac/Linux:**
```bash
export ANTHROPIC_API_KEY="sk-ant-api03-your-key-here"
```

Add to `~/.bashrc` or `~/.zshrc` to persist:
```bash
echo 'export ANTHROPIC_API_KEY="sk-ant-api03-your-key-here"' >> ~/.zshrc
source ~/.zshrc
```

**Windows:**
```cmd
set ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

### Option 2: .env File

Create a `.env` file in the repo (don't commit this!):
```
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

The `.gitignore` already excludes `.env` files.

### Option 3: Pass Directly (Not Recommended)

Some scripts accept `--api-key` argument:
```bash
python extract.py ~/photos ~/output.csv --api-key sk-ant-api03-xxx
```

⚠️ This leaves your key in terminal history.

## Testing Your Key

Run this to verify:
```bash
python -c "import anthropic; c = anthropic.Anthropic(); print('Connected!')"
```

If you see "Connected!" your key is working.

## Common Errors

### "Invalid API key"
- Check for extra spaces or line breaks in your key
- Make sure you copied the complete key
- Verify the key hasn't been revoked

### "Insufficient funds"
- Add credits to your Anthropic account
- Check your spending limit

### "Rate limit exceeded"
- Wait a few minutes and try again
- Add delays between API calls

## Cost Monitoring

Check your usage at [console.anthropic.com/usage](https://console.anthropic.com/usage)

### Estimated Costs
| Model | Cost per Image |
|-------|---------------|
| Claude Sonnet 4 | ~$0.02-0.05 |
| Claude Opus 4.5 | ~$0.15-0.40 |

### Setting Limits

1. Go to **Settings** → **Limits**
2. Set a monthly spending cap
3. Set up usage alerts

## Security Best Practices

1. **Never commit API keys** to git
2. **Don't share keys** between team members - each person should have their own
3. **Rotate keys** if you suspect they've been exposed
4. **Use environment variables** rather than hardcoding
5. **Set spending limits** to prevent unexpected charges
