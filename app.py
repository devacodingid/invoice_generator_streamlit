import streamlit as st
import psycopg2
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

# Function to connect to the PostgreSQL (Supabase) database
def get_invoice_data(invoice_ref_no):
    # Connect to your Supabase/PostgreSQL database
    conn = psycopg2.connect(
        dbname="your_db_name", user="your_db_user", password="your_db_password", host="your_db_host", port="5432"
    )
    cur = conn.cursor()

    # Query to fetch invoice data
    query = f"""
    SELECT ref_no, financial_year, invoice_no, invoice_date, bill_period, client_id, description_1, sub_total_1, 
           description_2, sub_total_2, total
    FROM invoices
    WHERE ref_no = %s;
    """
    cur.execute(query, (invoice_ref_no,))
    invoice_data = cur.fetchone()
    cur.close()
    conn.close()

    return invoice_data

# Function to generate a PDF of the invoice
def generate_invoice_pdf(invoice_data):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # Set up fonts
    c.setFont("Helvetica", 12)

    # Extract data from invoice
    ref_no, financial_year, invoice_no, invoice_date, bill_period, client_id, description_1, sub_total_1, description_2, sub_total_2, total = invoice_data
    
    # Write the invoice data onto the PDF
    c.drawString(100, 750, f"Invoice Number: {invoice_no}")
    c.drawString(100, 730, f"Financial Year: {financial_year}")
    c.drawString(100, 710, f"Invoice Date: {invoice_date}")
    c.drawString(100, 690, f"bill_period: {bill_period}")
    c.drawString(100, 670, f"Client ID: {client_id}")
    
    c.drawString(100, 630, f"Description 1: {description_1}")
    c.drawString(100, 610, f"Subtotal 1: ${sub_total_1}")
    
    c.drawString(100, 590, f"Description 2: {description_2}")
    c.drawString(100, 570, f"Subtotal 2: ${sub_total_2}")
    
    c.drawString(100, 530, f"Total: ${total}")
    
    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer

# Streamlit interface
def main():
    st.title("Invoice Generator")

    # Input: Invoice reference number
    invoice_ref_no = st.number_input("Enter Invoice Reference Number", min_value=1, step=1)

    if st.button("Generate Invoice"):
        # Fetch invoice data from database
        invoice_data = get_invoice_data(invoice_ref_no)
        
        if invoice_data:
            # Generate PDF
            pdf_buffer = generate_invoice_pdf(invoice_data)

            # Provide download link
            st.download_button(
                label="Download Invoice PDF",
                data=pdf_buffer,
                file_name=f"invoice_{invoice_ref_no}.pdf",
                mime="application/pdf"
            )
        else:
            st.error("Invoice not found.")

if __name__ == "__main__":
    main()
