
def extract_text(path: str) -> str:
    """
    Main function to read a PDF file and extract text from it.
    
    Args:
        path (str): The path to the PDF file.
    
    Returns:
        str: The extracted text from the PDF file.
    """
    import PyPDF2

    # Open the PDF file
    with open(path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        
        # Iterate through each page and extract text
        for page in reader.pages:
            text += page.extract_text()
    
    return text


if __name__ == "__main__":
    # Example usage
    pdf_path = "test/Lodovico_Satana.pdf"  # Replace with your PDF file path
    extracted_text = extract_text(pdf_path)
    print(extracted_text[:10000])