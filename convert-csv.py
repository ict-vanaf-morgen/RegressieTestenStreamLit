import pandas as pd
from fpdf import FPDF

# CSV inlezen
df = pd.read_csv(r"C:/Users/luke/Documents/GitHub/ST_reg_overzicht/data/2025-10-01T11-48_export.csv")

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Testcase Export', 0, 1, 'C')

pdf = PDF()
pdf.add_page()
pdf.set_font("Arial", size=10)

# Header rij
for col_name in df.columns:
    pdf.cell(40, 10, col_name, 1, 0, 'C')
pdf.ln()

# Data rijen
for row in df.itertuples(index=False):
    for item in row:
        text = str(item) if pd.notnull(item) else ""
        pdf.cell(40, 10, text, 1, 0, 'C')
    pdf.ln()

pdf.output("output_testcases.pdf")
