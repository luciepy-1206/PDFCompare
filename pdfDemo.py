import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
from PyPDF2 import PdfReader
from difflib import SequenceMatcher
import os

st.set_page_config(layout="wide")
st.title("PDF Comparison with Side-by-Side Layout & Similarity Percentage")

def extract_text_from_pdf(uploaded_file):
    pdf = PdfReader(uploaded_file)
    text = ""
    for page in pdf.pages:
        text += page.extract_text() or ""
    return text

def calc_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def base_name(filename):
    return os.path.splitext(filename)[0]

files1 = st.file_uploader("Upload PDFs for Set 1", type="pdf", accept_multiple_files=True)
files2 = st.file_uploader("Upload PDFs for Set 2", type="pdf", accept_multiple_files=True)

pairs = []
results = {}
skipped_pairs = []

if files1 and files2:
    for f1 in files1:
        base1 = base_name(f1.name)
        best_match = None
        highest_score = 0.0
        for f2 in files2:
            base2 = base_name(f2.name)
            score = calc_similarity(base1, base2)
            if score > highest_score and base1 != base2:
                highest_score = score
                best_match = f2
        if best_match and highest_score > 0.5:
            pairs.append((f1, best_match, highest_score))
    
    st.write(f"Found {len(pairs)} file pairs by filename similarity.")
    
    if pairs:
        if st.button("Run Comparison"):
            for f1, f2, _ in pairs:
                # Read PDF bytes for display
                f1_bytes = f1.read()
                f1.seek(0)
                f2_bytes = f2.read()
                f2.seek(0)
                
                # Extract text to compute similarity %
                text1 = extract_text_from_pdf(f1)
                text2 = extract_text_from_pdf(f2)
                similarity_ratio = calc_similarity(text1, text2)
                
                # Skip if similarity is greater than 98%
                if similarity_ratio > 0.98:
                    skipped_pairs.append((f1.name, f2.name, similarity_ratio))
                    continue
                
                results[(f1.name, f2.name)] = (similarity_ratio, f1_bytes, f2_bytes)
            
            # Display skipped pairs
            if skipped_pairs:
                st.success(f"Skipped {len(skipped_pairs)} pair(s) with >98% similarity:")
                for name1, name2, sim_score in skipped_pairs:
                    st.write(f"• {name1} vs {name2}: {sim_score*100:.2f}%")
            
            # Display compared pairs
            if results:
                st.write(f"Displaying {len(results)} pair(s) with ≤98% similarity:")
                for (name1, name2), (sim_score, bytes1, bytes2) in results.items():
                    st.subheader(f"Comparing {name1} vs {name2}")
                    st.write(f"Text Similarity: {sim_score*100:.2f} %")
                    col1, col2 = st.columns(2, gap="medium")
                    with col1:
                        st.write(name1)
                        pdf_viewer(bytes1, width="100%")
                    with col2:
                        st.write(name2)
                        pdf_viewer(bytes2, width="100%")
            elif not skipped_pairs:
                st.info("No results to display.")
    else:
        st.warning("No suitable file pairs found with enough filename similarity.")
else:
    st.info("Please upload PDF files to both sets to enable comparison.")
