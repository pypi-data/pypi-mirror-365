# GitHub Actions Quick Start

This guide helps you set up GitHub Actions for the Ray Simplify project in just a few minutes.

## ✅ What You Get

- **Automated Testing**: Runs on every push and PR
- **Code Quality**: Black formatting and Ruff linting
- **Security Scanning**: Vulnerability detection
- **Package Building**: Automatic wheel and source distribution creation
- **PyPI Publishing**: Automatic publishing on version tags
- **Cross-Platform Testing**: Ubuntu, Windows, macOS support

## 🚀 Setup Steps

### 1. Enable GitHub Actions (if not already enabled)

GitHub Actions is enabled by default for public repositories. For private repositories:
1. Go to Settings → Actions → General
2. Select "Allow all actions and reusable workflows"

### 2. Set Up PyPI Publishing (Optional)

To enable automatic PyPI publishing:

1. **Get PyPI API Token:**
   - Go to [PyPI Account Settings](https://pypi.org/manage/account/token/)
   - Create new API token with scope for this project
   - Copy the token (starts with `pypi-`)

2. **Add Repository Secret:**
   - Go to your repo → Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `PYPI_API_TOKEN`
   - Value: Your PyPI token

3. **Create Release Environment:**
   - Go to Settings → Environments
   - Click "New environment"
   - Name: `release`
   - Add protection rules if desired (optional)

### 3. Test the Setup

1. **Make a small change** to trigger the workflow:
   ```bash
   # Add a comment or update README
   git add .
   git commit -m "test: trigger GitHub Actions"
   git push
   ```

2. **Check the workflow:**
   - Go to Actions tab in your repository
   - You should see "CI/CD Pipeline" running
   - Click on it to see progress

### 4. Create Your First Release

When ready to publish:

1. **Update version** in `src/ray_simplify/__init__.py`
2. **Commit and push:**
   ```bash
   git add .
   git commit -m "release: version 0.1.1"
   git push
   ```
3. **Create and push tag:**
   ```bash
   git tag v0.1.1
   git push origin v0.1.1
   ```

The package will automatically:
- Build and test
- Publish to PyPI
- Create GitHub release

## 📊 Add Status Badges

Add these to your README.md for instant status visibility:

```markdown
[![CI/CD](https://github.com/DINHDUY/ray-simplify/actions/workflows/ci.yml/badge.svg)](https://github.com/DINHDUY/ray-simplify/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/ray-simplify.svg)](https://badge.fury.io/py/ray-simplify)
```

## 🔧 Customization

### Change Python Versions

Edit `.github/workflows/ci.yml`:
```yaml
strategy:
  matrix:
    python-version: ['3.11', '3.12']  # Add/remove versions
```

### Disable Nightly Tests

If you don't need nightly testing, delete `.github/workflows/nightly.yml`

### Add Code Coverage Badge

1. Sign up at [Codecov](https://codecov.io)
2. Add `CODECOV_TOKEN` to repository secrets
3. Add badge: `[![Coverage](https://codecov.io/gh/DINHDUY/ray-simplify/branch/main/graph/badge.svg)](https://codecov.io/gh/DINHDUY/ray-simplify)`

## 🐛 Troubleshooting

### Workflow Fails
- Check the Actions tab for error details
- Common issues: dependency problems, test failures, formatting issues

### PyPI Publishing Fails
- Verify `PYPI_API_TOKEN` secret is set correctly
- Ensure version number is incremented
- Check if package name is available on PyPI

### Tests Fail Locally But Pass in CI
- Ensure you're using the same Python version
- Check environment-specific issues (paths, dependencies)

## 📚 Next Steps

1. ✅ Set up branch protection rules
2. ✅ Configure Dependabot for security updates
3. ✅ Add more comprehensive tests
4. ✅ Set up deployment environments
5. ✅ Configure notification settings

For more detailed information, see the full [GitHub Actions documentation](.github/README.md).
