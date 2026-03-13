# Process Inbox Files

Process files dropped in the Inbox folder and create action items.

## Description

This skill monitors the Inbox folder for new files and automatically creates action items in the Needs_Action folder with appropriate metadata and suggested actions based on file type.

## Usage

```
/process-inbox
```

## What it does

1. Scans the Inbox folder for new files
2. Analyzes file type and size
3. Creates a structured action item in Needs_Action
4. Suggests appropriate next steps based on file type

## File Types Handled

- **Spreadsheets** (.csv, .xlsx, .xls): Import to accounting, generate reports
- **Documents** (.pdf, .doc, .docx): Review and extract information
- **Images** (.jpg, .png, .gif): Add to media library
- **Other files**: General review and processing
