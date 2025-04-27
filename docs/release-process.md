# Release Process

This document outlines the process for releasing new versions of `wagtail-unveil` to PyPI.

## Prerequisites

Before you can release a new version, ensure you have:

1. GitHub repository access with permissions to create releases
2. PyPI account with publishing rights to the `wagtail-unveil` package

## Release Steps

### 1. Update Version

1. Update the version number in `pyproject.toml`:
   ```python
   [project]
   name = "wagtail-unveil"
   version = "x.y.z"  # Update this line
   ```

2. Update any version references in documentation if applicable

### 2. Update Changelog

1. Make sure the `CHANGELOG.md` file is updated with all notable changes for the new version:
   - New features
   - Bug fixes
   - Breaking changes
   - Deprecations

### 3. Create and Push a Release Commit

1. Commit the version and changelog updates:
   ```bash
   git add pyproject.toml CHANGELOG.md
   git commit -m "Prepare release x.y.z"
   git push origin main
   ```

### 4. Create a GitHub Release

1. Go to the GitHub repository
2. Click on "Releases" and then "Create a new release"
3. Create a new tag in the format `vx.y.z` (e.g., `v0.1.0`)
4. Title the release with the version number (e.g., "v0.1.0")
5. Copy the relevant section from the CHANGELOG.md into the description
6. Click "Publish release"

### 5. Automated PyPI Release

Once the GitHub release is created, the GitHub Actions workflow will automatically:

1. Build the package
2. Publish it to PyPI

The workflow is defined in `.github/workflows/publish.yml` and is triggered by the creation of a new release.

### 6. Verify the Release

After the workflow completes:

1. Check the GitHub Actions logs to ensure the build and publish steps completed successfully
2. Verify the package is available on PyPI at https://pypi.org/project/wagtail-unveil/
3. Consider installing the package in a clean environment to test that the release works as expected:
   ```bash
   pip install wagtail-unveil==x.y.z
   ```

## Troubleshooting

If the automated release fails:

1. Check the GitHub Actions logs for errors
2. Make necessary corrections
3. If needed, delete the GitHub release and try again with a new patch version

## Post-Release Tasks

1. Update the development version in `pyproject.toml` to the next anticipated version with a `.dev0` suffix
2. Create a new section in the CHANGELOG.md for the next version
3. Announce the release to the appropriate channels (if applicable)