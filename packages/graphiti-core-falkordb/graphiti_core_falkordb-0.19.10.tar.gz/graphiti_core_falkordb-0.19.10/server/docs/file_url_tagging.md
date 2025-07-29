# File URL Tagging for Message Ingestion

This document explains how to tag file URLs and metadata when ingesting messages through the Graphiti API.

## Overview

When ingesting content from files (PDFs, documents, web pages, etc.), you can now tag the source URL and metadata to maintain traceability and enable source-based retrieval.

## Enhanced Message Model

The `Message` model now supports additional source tracking fields:

```json
{
  "content": "Document content here...",
  "role_type": "system",
  "role": "Document Parser",
  "source_description": "Quarterly financial report",
  "source_url": "https://example.com/docs/q4-2024-report.pdf",
  "source_metadata": {
    "file_size": "2.5MB",
    "file_type": "PDF",
    "page_count": 45,
    "extraction_method": "OCR",
    "confidence_score": 0.95
  }
}
```

### New Fields

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `source_url` | string | URL or file path of the source document | No |
| `source_metadata` | object | Additional metadata about the source | No |

## Usage Examples

### 1. PDF Document Ingestion

```json
{
  "group_id": "document_analysis_123",
  "messages": [
    {
      "content": "Executive Summary: Our Q4 2024 revenue increased by 15%...",
      "role_type": "system",
      "role": "PDF Extractor",
      "source_description": "Q4 2024 Financial Report - Executive Summary",
      "source_url": "https://company.com/reports/q4-2024-financial.pdf",
      "source_metadata": {
        "file_size": "3.2MB",
        "file_type": "PDF",
        "page_count": 52,
        "section": "Executive Summary",
        "pages": "1-3",
        "extraction_method": "PyPDF2",
        "extraction_timestamp": "2024-01-15T10:30:00Z"
      }
    }
  ]
}
```

### 2. Web Page Content

```json
{
  "group_id": "web_research_456",
  "messages": [
    {
      "content": "Latest developments in AI research show significant progress...",
      "role_type": "system",
      "role": "Web Scraper",
      "source_description": "AI Research News Article",
      "source_url": "https://techcrunch.com/2024/01/15/ai-breakthrough",
      "source_metadata": {
        "domain": "techcrunch.com",
        "article_date": "2024-01-15",
        "author": "John Smith",
        "word_count": 1250,
        "scraping_method": "BeautifulSoup",
        "last_updated": "2024-01-15T14:22:00Z"
      }
    }
  ]
}
```

### 3. Local File Processing

```json
{
  "group_id": "local_docs_789",
  "messages": [
    {
      "content": "Meeting notes from the product planning session...",
      "role_type": "system",
      "role": "File Reader",
      "source_description": "Product Planning Meeting Notes",
      "source_url": "file:///Users/john/Documents/meetings/product-planning-2024-01-15.md",
      "source_metadata": {
        "file_size": "15KB",
        "file_type": "Markdown",
        "created_date": "2024-01-15T09:00:00Z",
        "modified_date": "2024-01-15T11:30:00Z",
        "encoding": "UTF-8",
        "line_count": 342
      }
    }
  ]
}
```

### 4. Email Processing

```json
{
  "group_id": "email_analysis_101",
  "messages": [
    {
      "content": "Subject: Project Update\nFrom: alice@company.com\nDear team, here's the latest update...",
      "role_type": "system",
      "role": "Email Parser",
      "source_description": "Project update email from Alice",
      "source_url": "mailto:alice@company.com",
      "source_metadata": {
        "message_id": "<abc123@company.com>",
        "sender": "alice@company.com",
        "recipients": ["team@company.com"],
        "subject": "Project Update",
        "sent_date": "2024-01-15T08:45:00Z",
        "email_client": "Outlook",
        "has_attachments": false
      }
    }
  ]
}
```

## Source Information Storage

The source information is stored in the `EpisodicNode` with an enhanced `source_description` field that combines:

1. **Original description**: Your provided `source_description`
2. **Source URL**: Appended as `| Source URL: {url}`
3. **Metadata**: Appended as `| Metadata: key1: value1, key2: value2`

Example stored format:
```
"Quarterly financial report | Source URL: https://example.com/q4-report.pdf | Metadata: file_size: 2.5MB, file_type: PDF, page_count: 45"
```

## Retrieval and Search

### 1. Search by Source URL

You can search for content from specific sources:

```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Source URL: https://example.com/q4-report.pdf",
    "max_facts": 20
  }'
```

### 2. Search by File Type

```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "file_type: PDF",
    "max_facts": 50
  }'
```

### 3. Entity Context with Source Information

When using the entity context endpoint, source information appears in the episodic context:

```json
{
  "entity_uuid": "...",
  "context": "...\n=== EPISODIC CONTEXT ===\n• Episode: Q4 Financial Analysis\n  Source: Quarterly financial report | Source URL: https://example.com/q4-report.pdf\n  Content: Executive summary shows 15% revenue growth..."
}
```

## Best Practices

### 1. Consistent URL Formats

Use consistent URL formats for better searchability:

- **Web URLs**: `https://domain.com/path/file.ext`
- **Local files**: `file:///absolute/path/to/file.ext`
- **Cloud storage**: `s3://bucket/path/file.ext` or `gs://bucket/path/file.ext`
- **Email**: `mailto:sender@domain.com` or `imap://server/folder/message-id`

### 2. Useful Metadata Fields

Include relevant metadata for your use case:

**For Documents:**
- `file_size`, `file_type`, `page_count`
- `creation_date`, `modification_date`
- `author`, `title`, `version`

**For Web Content:**
- `domain`, `article_date`, `author`
- `word_count`, `last_updated`
- `scraping_method`, `content_type`

**For Emails:**
- `sender`, `recipients`, `subject`
- `message_id`, `sent_date`
- `has_attachments`, `thread_id`

### 3. Batch Processing

When processing multiple files, maintain consistent metadata structure:

```python
import requests

files_to_process = [
    {
        "path": "/docs/report1.pdf",
        "url": "https://storage.com/report1.pdf",
        "content": "...",
        "metadata": {"file_type": "PDF", "page_count": 25}
    },
    {
        "path": "/docs/report2.pdf", 
        "url": "https://storage.com/report2.pdf",
        "content": "...",
        "metadata": {"file_type": "PDF", "page_count": 18}
    }
]

messages = []
for file_info in files_to_process:
    messages.append({
        "content": file_info["content"],
        "role_type": "system",
        "role": "Document Processor",
        "source_description": f"Document: {file_info['path']}",
        "source_url": file_info["url"],
        "source_metadata": file_info["metadata"]
    })

response = requests.post("http://localhost:8000/messages", json={
    "group_id": "document_batch_123",
    "messages": messages
})
```

## Integration Examples

### Python File Processing

```python
import os
import requests
from datetime import datetime

def ingest_file(file_path: str, content: str, base_url: str = "https://storage.com"):
    file_stats = os.stat(file_path)
    file_url = f"{base_url}/{os.path.basename(file_path)}"
    
    message = {
        "content": content,
        "role_type": "system",
        "role": "File Processor",
        "source_description": f"Processed file: {os.path.basename(file_path)}",
        "source_url": file_url,
        "source_metadata": {
            "file_size": f"{file_stats.st_size / 1024:.1f}KB",
            "file_type": os.path.splitext(file_path)[1].upper().lstrip('.'),
            "created_date": datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
            "modified_date": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
            "full_path": file_path
        }
    }
    
    response = requests.post("http://localhost:8000/messages", json={
        "group_id": "file_processing",
        "messages": [message]
    })
    
    return response.json()
```

This enhanced file URL tagging system provides comprehensive source tracking for all your ingested content, enabling better traceability and source-based analysis in your knowledge graph.
