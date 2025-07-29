import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime
import os
def load_data(file_path):
    """
    Load data from various file formats: CSV, Excel, JSON, TXT.
    Returns a pandas DataFrame.
    """
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext == '.csv':
            return pd.read_csv(file_path)
        elif ext == '.xlsx':
            return pd.read_excel(file_path)
        elif ext == '.json':
            return pd.read_json(file_path)
        elif ext == '.txt':
            # Try both comma and tab delimiters
            try:
                return pd.read_csv(file_path, delimiter='\t')
            except:
                return pd.read_csv(file_path, delimiter=',')
        else:
            raise ValueError("Unsupported file format: " + ext)
    except Exception as e:
        raise RuntimeError(f"Error loading file: {e}")
# === Setup Directories ===
os.makedirs("charts", exist_ok=True)

# === Load Data ===
file_path = "d:\CODTechITIntern\Task2\sales_data.csv"  # or .xlsx, .json, .txt
df = load_data(file_path)
print(df.head())
df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
df["Total Sales"] = df["Units Sold"] * df["Unit Price"]

# === Basic Analysis ===
total_units = df["Units Sold"].sum()
total_sales = df["Total Sales"].sum()
product_sales = df.groupby("Product")["Total Sales"].sum()

# === Chart Generation ===
plt.figure(figsize=(6, 4))
product_sales.plot(kind="bar", color="skyblue")
plt.title("Total Sales by Product")
plt.ylabel("Sales (INR)")
plt.tight_layout()
plt.savefig("charts/sales_by_product.png")
plt.close()

# === PDF Report ===
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "Sales Report", ln=True, align="C")
        self.set_font("Arial", "", 12)
        self.cell(0, 10, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
        self.ln(10)

    def chapter_title(self, title):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, title, ln=True)
        self.ln(5)

    def chapter_body(self, text):
        self.set_font("Arial", "", 12)
        self.multi_cell(0, 10, text)
        self.ln()

    def add_image(self, image_path, w=150):
        self.image(image_path, w=w)
        self.ln()

pdf = PDF()
pdf.add_page()

pdf.chapter_title("Summary")
summary = f"Total Units Sold: {total_units}\nTotal Sales: INR {total_sales:,.2f}"
pdf.chapter_body(summary)

pdf.chapter_title("Sales by Product")
pdf.add_image("charts/sales_by_product.png")

pdf.output("d:\CODTechITIntern\Task2\sales_report1.pdf")
print("✅ Report Generated: sales_report1.pdf")
