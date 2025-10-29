# GitHub Actions Workflows

This directory contains automated workflows for the UPSS project.

## Workflows

### Zenodo Metadata Update (`zenodo-metadata-update.yml`)

**Purpose**: Automatically updates Zenodo metadata when a new release is published.

**Trigger**: Runs automatically when a GitHub release is published.

**What it does**:
1. Extracts release information (version, date, description)
2. Updates the `CITATION.cff` file with the new version and release date
3. Creates Zenodo-compatible metadata from the release information
4. Checks for existing unpublished drafts and deletes them automatically
5. Creates a new version on Zenodo
6. Deletes inherited files from the new draft version to prevent validation errors
7. Updates the metadata and publishes the new version
8. Provides a summary with the new DOI

**Required Secrets**:

To enable automatic Zenodo updates, add the following secrets to your repository:

1. **`ZENODO_ACCESS_TOKEN`**: Your Zenodo personal access token
   - Go to https://zenodo.org/account/settings/applications/tokens/new/
   - Create a token with `deposit:write` and `deposit:actions` scopes
   - Add it as a repository secret in Settings > Secrets and variables > Actions

2. **`ZENODO_DEPOSITION_ID`**: The ID of your Zenodo deposition
   - This is the numeric ID from your Zenodo record URL
   - Example: For https://doi.org/10.5281/zenodo.17472647, use `17472647`
   - Add it as a repository secret in Settings > Secrets and variables > Actions

**Usage**:

The workflow runs automatically when you publish a release. To create a release:

```bash
# Tag the release
git tag -a v1.1.0 -m "Release v1.1.0"
git push origin v1.1.0

# Create a release on GitHub
# Go to https://github.com/alvinveroy/prompt-security-standard/releases/new
# Or use GitHub CLI:
gh release create v1.1.0 --title "v1.1.0" --notes "Release notes here"
```

**Behavior without secrets**:

If the required secrets are not configured, the workflow will:
- Still run successfully
- Update the CITATION.cff file
- Skip the Zenodo update steps with a warning message
- Provide instructions for configuring the secrets

This allows the workflow to work without breaking CI/CD while providing clear guidance for enabling full functionality.

**Metadata-only records**:

The workflow creates metadata-only records on Zenodo, meaning no files are uploaded to Zenodo. This approach is appropriate because:

1. **GitHub as primary source**: UPSS is a GitHub-hosted standard, and the repository serves as the authoritative source for all files and documentation
2. **DOI assignment**: Zenodo is used primarily for assigning DOIs and providing citation metadata for academic and research purposes
3. **Reference linking**: The metadata includes links back to the GitHub repository, ensuring users always access the most current version
4. **File management**: Setting `files.enabled: false` in the metadata prevents file duplication and ensures Zenodo doesn't attempt to host repository files

This metadata-only approach maintains a single source of truth on GitHub while leveraging Zenodo's DOI and citation infrastructure for academic recognition and discoverability.

**Workflow outputs**:

- Updated `CITATION.cff` file (if needed)
- New Zenodo version with updated metadata
- New DOI for the release
- Summary in the GitHub Actions UI

**Security considerations**:

- The workflow uses `permissions: contents: read` for minimal access
- Secrets are never exposed in logs
- All API communication uses HTTPS
- The access token is only used for the Zenodo API

**Troubleshooting**:

If the workflow fails:

1. **Check secrets**: Ensure `ZENODO_ACCESS_TOKEN` and `ZENODO_DEPOSITION_ID` are set correctly
2. **Verify token scopes**: The token needs `deposit:write` and `deposit:actions` scopes
3. **Check Zenodo status**: Verify your Zenodo record exists and is accessible
4. **Review logs**: Check the workflow run logs for specific error messages
5. **ORCID validation errors**: Note that ORCID identifiers are intentionally omitted from the metadata to avoid validation issues with Zenodo's API. The ORCID is maintained in CITATION.cff for proper citation format.
6. **Test locally**: You can test the API calls locally:

```bash
# Test creating a new version
curl -X POST \
  "https://zenodo.org/api/deposit/depositions/YOUR_DEPOSITION_ID/actions/newversion" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Common Issues**:

- **Invalid ORCID identifier**: If you see this error, it's because Zenodo's API has specific requirements for ORCID format. The workflow intentionally omits ORCID from the API payload to avoid this issue.
- **DOI is null**: This indicates the publish step failed. Check the publish response for validation errors.
- **400 Bad Request**: Usually indicates invalid metadata format. Review the error messages in the workflow logs.
- **"Please remove all files first" error**: The workflow now automatically handles existing unpublished drafts by deleting them before creating a new version. This prevents stale drafts from causing validation errors. If you encounter this error, check that the draft deletion step completed successfully in the workflow logs.

**Testing**:

To test the workflow without creating an actual release:

1. Create a test tag: `git tag -a test-v1.0.1 -m "Test release"`
2. Push the tag: `git push origin test-v1.0.1`
3. Create a pre-release on GitHub using this tag
4. Verify the workflow runs (it will skip Zenodo update without secrets)
5. Delete the test release and tag after verification

**Related documentation**:

- [Zenodo API Documentation](https://developers.zenodo.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [CITATION.cff Format](https://citation-file-format.github.io/)
