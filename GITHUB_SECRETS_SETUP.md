# GitHub Secrets Setup Guide

This guide explains how to add your Huckleberry credentials as GitHub secrets for CI/CD integration tests.

## Required Secrets

The integration tests require two secrets:

1. `HUCKLEBERRY_EMAIL` - Your Huckleberry account email
2. `HUCKLEBERRY_PASSWORD` - Your Huckleberry account password

## Adding Secrets to GitHub

### Step 1: Navigate to Settings

1. Go to your GitHub repository
2. Click on **Settings** (top navigation)
3. In the left sidebar, click on **Secrets and variables** → **Actions**

### Step 2: Add New Repository Secret

For each secret:

1. Click the **New repository secret** button
2. Enter the **Name**: `HUCKLEBERRY_EMAIL`
3. Enter the **Secret**: Your Huckleberry account email
4. Click **Add secret**

Repeat for `HUCKLEBERRY_PASSWORD`.

### Step 3: Verify Secrets

After adding both secrets, you should see:
- ✓ `HUCKLEBERRY_EMAIL`
- ✓ `HUCKLEBERRY_PASSWORD`

## Security Best Practices

⚠️ **Important Security Notes:**

1. **Use a Test Account**: Create a separate Huckleberry account for testing, not your personal baby tracking account
2. **Never Commit Credentials**: Never commit credentials to the repository
3. **Rotate Regularly**: Consider changing the test account password periodically
4. **Limited Access**: Only give the test account access to test data

## Testing the Setup

Once secrets are added:

1. Push a commit to the `main` branch
2. Go to **Actions** tab in your repository
3. Watch the **Integration Tests** workflow run
4. Verify it completes successfully

## Troubleshooting

### Workflow Fails with "Authentication failed"

**Possible causes:**
- Incorrect email or password in secrets
- Account credentials changed
- Account locked or disabled

**Solution:**
- Double-check credentials are correct
- Update the secrets with correct values
- Try logging into Huckleberry app to verify account works

### Workflow Fails with "No children found"

**Possible causes:**
- Test account has no child profiles

**Solution:**
- Add at least one child profile to the test account
- Use the Huckleberry mobile app to create a child

### Tests Timeout or Fail Intermittently

**Possible causes:**
- Firebase network issues
- Rate limiting
- Slow CI runner

**Solution:**
- Re-run the workflow
- Check Firebase/Huckleberry service status
- Consider adding retry logic

## Running Tests Locally

To test locally before pushing:

```powershell
# Set environment variables
$env:HUCKLEBERRY_EMAIL = "test@example.com"
$env:HUCKLEBERRY_PASSWORD = "test-password"

# Run the test script
.\run-tests.ps1
```

Or manually:

```powershell
uv sync --dev
uv run pytest tests/test_integration.py -v
```

## Workflow Configuration

The workflow file is located at:
```
.github/workflows/integration-tests.yml
```

It runs on:
- Every push to `main` branch
- Every pull request to `main` branch
- Manual trigger (workflow_dispatch)

Tests run on Python versions: 3.9, 3.10, 3.11, 3.12

## Need Help?

If you encounter issues:

1. Check the Actions logs for detailed error messages
2. Review the test output in the workflow run
3. Ensure secrets are correctly named and set
4. Verify the test account works by logging in manually
5. Open an issue in the repository if problems persist
