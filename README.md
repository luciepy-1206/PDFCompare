# Streamlit PDF Comparison Tool

This is a Streamlit web application that lets you upload two sets of PDF files, auto-pairs them by filename similarity, and visually compares the paired documents side-by-side. It also calculates and displays a similarity percentage based on the extracted text content.

## Features

- Upload and drag/drop PDF files directly in the app.
- Auto-pair PDFs based on filename similarity excluding suffixes.
- Visual side-by-side PDF viewers for manual comparison.
- Displays a computed text similarity percentage for each pair.
- Responsive two-column layout stretching each viewer to fill half the page width.

## Requirements

- Python 3.7+
- Streamlit
- PyPDF2
- streamlit-pdf-viewer
