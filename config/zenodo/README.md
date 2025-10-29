# Zenodo Metadata Configuration

This directory contains externalized Zenodo metadata for the Universal Prompt Security Standard (UPSS) repository, following the project's principle of separation of concerns.

## Files

### `metadata.json`

The complete Zenodo metadata configuration file that defines how UPSS is published and indexed on Zenodo for academic citation and discoverability.

**Purpose**: Separate metadata from workflow code for better maintainability, version control, and review.

## Structure

The metadata file follows the Zenodo API specification and includes:

### Core Metadata
- **title**: Project title
- **upload_type**: Type of content (software)
- **publication_date**: Release date (dynamically injected)
- **version**: Version number (dynamically injected)
- **language**: Language code (eng for English)
- **description**: Comprehensive project description
- **license**: Software license (MIT)
- **access_right**: Access level (open)

### Academic Metadata
- **creators**: Authors/creators list
- **contributors**: Contributors with role types
- **keywords**: Searchable keywords array
- **subjects**: Controlled Library of Congress subject headings
- **method**: Research/development methodology description

### Related Resources
- **related_identifiers**: Links to GitHub repository, issues, discussions
- **references**: Citations to related standards and frameworks

### Additional Information
- **notes**: Community contribution status and participation information

## Placeholders

The metadata file uses placeholders that are dynamically replaced during workflow execution:

- `{{VERSION}}`: Replaced with the release tag version
- `{{PUBLICATION_DATE}}`: Replaced with the release date in ISO 8601 format
- `{{RELEASE_BODY}}`: Replaced with the GitHub release notes

## Usage

### Updating Metadata

To update Zenodo metadata:

1. Edit `config/zenodo/metadata.json` directly
2. Commit and push changes
3. On the next release, the updated metadata will be published to Zenodo

### Testing Changes

To test metadata changes before release:

```bash
# Validate JSON syntax
cat config/zenodo/metadata.json | jq .

# Test placeholder replacement (example)
sed 's/{{VERSION}}/v1.0.0/g; s/{{PUBLICATION_DATE}}/2025-10-29/g; s/{{RELEASE_BODY}}/Test release/g' config/zenodo/metadata.json
```

## Workflow Integration

The metadata is loaded by the `.github/workflows/zenodo-metadata-update.yml` workflow during the release process:

1. Workflow loads `config/zenodo/metadata.json`
2. Replaces placeholders with actual release values
3. Submits metadata to Zenodo API
4. Publishes new version with DOI

## Best Practices

### DO
✅ Edit metadata directly in this file  
✅ Validate JSON syntax after changes  
✅ Use meaningful commit messages when updating  
✅ Review controlled vocabulary terms (subjects)  
✅ Keep description comprehensive but concise  

### DON'T
❌ Hardcode version or date values  
❌ Remove required fields  
❌ Use invalid controlled vocabulary values  
❌ Exceed field length limits  
❌ Include sensitive information  

## Field Constraints

### Required Fields
- `title`, `upload_type`, `publication_date`, `creators`, `description`, `access_right`, `license`

### Controlled Vocabularies

**upload_type values:**
- `publication`, `poster`, `presentation`, `dataset`, `image`, `video`, `software`, `lesson`, `physicalobject`, `other`

**access_right values:**
- `open`, `embargoed`, `restricted`, `closed`

**contributor type values:**
- `ContactPerson`, `DataCollector`, `DataCurator`, `DataManager`, `Distributor`, `Editor`, `HostingInstitution`, `Producer`, `ProjectLeader`, `ProjectManager`, `ProjectMember`, `RegistrationAgency`, `RegistrationAuthority`, `RelatedPerson`, `Researcher`, `ResearchGroup`, `RightsHolder`, `Supervisor`, `Sponsor`, `WorkPackageLeader`, `Other`

**relation values (related_identifiers):**
- `isCitedBy`, `cites`, `isSupplementTo`, `isSupplementedBy`, `isContinuedBy`, `continues`, `isDescribedBy`, `describes`, `hasMetadata`, `isMetadataFor`, `isNewVersionOf`, `isPreviousVersionOf`, `isPartOf`, `hasPart`, `isReferencedBy`, `references`, `isDocumentedBy`, `documents`, `isCompiledBy`, `compiles`, `isVariantFormOf`, `isOriginalFormof`, `isIdenticalTo`, `isAlternateIdentifier`, `isReviewedBy`, `reviews`, `isDerivedFrom`, `isSourceOf`, `requires`, `isRequiredBy`, `isObsoletedBy`, `obsoletes`

## Resources

- **Zenodo API Documentation**: https://developers.zenodo.org/
- **Library of Congress Subject Headings**: https://id.loc.gov/
- **DataCite Metadata Schema**: https://schema.datacite.org/
- **ISO 639-2 Language Codes**: https://www.loc.gov/standards/iso639-2/php/code_list.php

## Separation of Concerns

This externalized configuration embodies UPSS's core principle: **separate configuration from code**.

Just as UPSS advocates for externalizing prompts from application code:
- **Metadata** is separated from **workflow logic**
- **Configuration** is separated from **implementation**
- **Content** is separated from **automation**

This approach enables:
- Independent review of metadata changes
- Version control of configuration
- Easier collaboration and contribution
- Reduced risk of workflow errors
- Clear audit trail of metadata evolution

---

**Note**: This metadata configuration is automatically synchronized with Zenodo on each GitHub release. Manual Zenodo updates are not necessary.
