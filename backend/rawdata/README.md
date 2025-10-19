# Raw Data - Requirements Source Documents

This directory contains source documents for requirements extraction and traceability analysis in CALIDUS.

## Purpose

The `rawdata/` folder stores:
- **Regulatory standards** (FAA, EASA, UAE GCAA regulations)
- **Customer specifications**
- **System requirements documents**
- **Design documents**
- **Test specifications**
- **Certification standards**

These documents are processed by CALIDUS to:
1. Extract requirements
2. Generate traceability links
3. Perform compliance analysis
4. Create test coverage matrices
5. Identify gaps and ambiguities

## Current Documents

### Regulatory Standards

#### 14 CFR Part 23 - Airworthiness Standards: Normal Category Airplanes
- **File**: `14 CFR Part 23 (in effect on 3-31-2017).pdf`
- **Size**: 2.8 MB
- **Effective Date**: March 31, 2017
- **Authority**: FAA (Federal Aviation Administration)
- **Documentation**: [14_CFR_Part_23.md](./14_CFR_Part_23.md)
- **Status**: Ready for import

**Description**: FAA certification standards for normal category airplanes. Contains design, construction, and performance requirements for small aircraft certification.

---

## Document Organization

### Naming Convention

Use clear, descriptive filenames:
```
[Regulation/Standard]_[Part/Section]_[Version/Date].[extension]
```

Examples:
- `14_CFR_Part_23_2017-03-31.pdf`
- `DO-178C_v1.0.pdf`
- `UAE_GCAA_CAR_Part_23.pdf`
- `System_Requirements_Spec_v2.3.docx`

### Markdown Documentation

Each source document should have an accompanying `.md` file with:
- Document overview and metadata
- Regulatory context
- Processing status
- Traceability information
- Integration notes

## Supported File Formats

CALIDUS can process the following formats:

| Format | Extension | Support Level | Notes |
|--------|-----------|---------------|-------|
| PDF | `.pdf` | ✅ Full | OCR + text extraction |
| Word | `.docx` | ✅ Full | Native parsing |
| Excel | `.xlsx` | ✅ Full | Table extraction |
| CSV | `.csv` | ✅ Full | Structured data import |
| JSON | `.json` | ✅ Full | Direct data import |
| XML | `.xml` | ✅ Full | Schema-based parsing |
| Text | `.txt` | ✅ Full | Plain text parsing |
| DOORS | `.dng` | 🔶 Partial | Via export to supported format |
| ReqIF | `.reqif` | 🔶 Planned | Requirements interchange format |
| ENOVIA | N/A | ✅ Full | Direct PLM integration |

## Import Methods

### Method 1: ENOVIA Import (Recommended)

For documents already in ENOVIA PLM:

1. Open CALIDUS demo: http://localhost:3000/demo
2. Click **"Import from ENOVIA"** tab
3. Enter ENOVIA server details:
   - Server URL: `https://enovia.company.com`
   - Workspace: Your workspace name
   - Project ID: Project identifier
4. Click **"Connect & Import from ENOVIA"**

**Benefits**:
- ✅ Preserves all ENOVIA metadata
- ✅ Maintains traceability links
- ✅ Bi-directional sync capability
- ✅ Version control integration
- ✅ Bulk import support

### Method 2: Document Upload

For local files:

1. Open CALIDUS demo: http://localhost:3000/demo
2. Scroll to **"Upload Documents"** section (below "OR" divider)
3. Drag and drop file or click to browse
4. Select file from `rawdata/` folder
5. CALIDUS will process automatically

**Processing includes**:
- Text extraction (OCR for scanned PDFs)
- Requirement identification (SHALL/MUST/WILL statements)
- Automatic classification
- Requirement ID generation
- Traceability structure creation

## Expected Document Types

### Regulatory Standards
- **14 CFR** (FAA regulations)
- **EASA CS** (European Aviation Safety Agency standards)
- **UAE GCAA CAR** (UAE General Civil Aviation Authority regulations)
- **DO-178C** (Software considerations in airborne systems)
- **DO-254** (Hardware design assurance)
- **AS9100** (Quality management systems)

### Technical Specifications
- System Requirements Specifications (SRS)
- Interface Control Documents (ICD)
- Design Description Documents (DDD)
- Test Plans and Procedures
- Verification and Validation Plans

### Customer Documents
- Statement of Work (SOW)
- Customer Specifications
- Technical Data Packages (TDP)
- Contract Requirements

## Processing Workflow

```
┌─────────────────┐
│  Raw Document   │
│  (PDF/DOCX/etc) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Text           │
│  Extraction     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Requirement    │
│  Identification │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Classification │
│  & Categorization│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Traceability   │
│  Link Creation  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Database       │
│  Storage        │
└─────────────────┘
```

## Requirement Extraction

### Requirement Identification Patterns

CALIDUS identifies requirements using:
- **SHALL** statements (mandatory)
- **MUST** statements (mandatory)
- **WILL** statements (informative/declaration)
- **SHOULD** statements (recommended)
- **MAY** statements (optional)

### Requirement Classification

Extracted requirements are classified as:
- **AHLR**: Airworthiness/High-Level Requirements
- **SYS**: System Requirements
- **HW**: Hardware Requirements
- **SW**: Software Requirements
- **TEST**: Test Requirements
- **CERT**: Certification Requirements

## Data Security

### Sensitive Documents

If documents contain sensitive or proprietary information:
1. ✅ Add to `.gitignore` to prevent accidental commits
2. ✅ Use ENOVIA import for controlled access
3. ✅ Mark files as confidential in metadata
4. ✅ Restrict access in CALIDUS role-based access control

### Current `.gitignore` Settings

The following patterns are excluded from Git:
```gitignore
# Exclude all PDFs in rawdata
rawdata/*.pdf

# Exclude proprietary formats
rawdata/*.docx
rawdata/*.xlsx

# Include documentation
!rawdata/*.md
!rawdata/README.md
```

## Adding New Documents

### Checklist

When adding a new document:

1. [ ] Place file in `rawdata/` directory
2. [ ] Use consistent naming convention
3. [ ] Create accompanying `.md` documentation file
4. [ ] Update this README with document entry
5. [ ] Verify file is properly ignored by Git (if sensitive)
6. [ ] Test import in CALIDUS
7. [ ] Document any processing issues

### Template for New Document

Copy this template for new documents:

```markdown
# [Document Title]

## Document Information
- **File**: `filename.ext`
- **Size**: X.X MB
- **Date**: YYYY-MM-DD
- **Authority**: Organization
- **Status**: Ready for import

## Overview
[Brief description]

## Processing Notes
[Any special considerations]

## Metadata
| Field | Value |
|-------|-------|
| **Type** | Regulatory/Specification/etc |
| **Version** | X.X |
| **Status** | Active/Draft/Superseded |
```

## Known Issues

### PDF Parsing Challenges
- Scanned PDFs require OCR (slower processing)
- Multi-column layouts may need special handling
- Tables may require manual review
- Non-standard fonts can affect extraction

### Solutions
- Use searchable PDFs when possible
- Pre-process scanned documents with OCR
- Export tables to Excel for structured import
- Use ENOVIA import for complex documents

## Statistics

| Metric | Count |
|--------|-------|
| **Total Documents** | 1 |
| **Processed** | 0 |
| **Pending** | 1 |
| **File Size** | 2.8 MB |
| **Formats** | PDF (1) |

## Future Documents

### Planned Additions
- [ ] 14 CFR Part 21 (Certification Procedures)
- [ ] 14 CFR Part 25 (Transport Category)
- [ ] DO-178C (Software standard)
- [ ] DO-254 (Hardware standard)
- [ ] AS9100 Rev D (Quality management)
- [ ] UAE GCAA CAR-Part 23
- [ ] EASA CS-23
- [ ] Customer requirements documents

## Maintenance

### Regular Updates
- Check for new regulation versions quarterly
- Update documentation when documents are processed
- Archive superseded versions
- Maintain processing status

### Backup
- Source documents should be backed up separately
- Use version control for `.md` documentation
- Consider cloud storage for large files
- Keep original unmodified copies

## Support

For questions or issues:
- **Documentation**: See [CLAUDE.md](../CLAUDE.md)
- **Issues**: https://github.com/zozisteam/cls-requirement_management/issues
- **Wiki**: Project documentation in repository

---

**Last Updated**: 2025-10-17
**Maintained By**: CALIDUS Development Team
**Total Documents**: 1 (2.8 MB)
