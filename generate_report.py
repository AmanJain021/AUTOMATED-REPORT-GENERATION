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
            try:
                return pd.read_csv(file_path, delimiter='\t')
            except:
                return pd.read_csv(file_path, delimiter=',')
        else:
            raise ValueError("Unsupported file format: " + ext)
    except Exception as e:
        raise RuntimeError(f"Error loading file: {e}")

# === Setup Directory ===
os.makedirs("charts", exist_ok=True)

# === Load Data ===
file_path = "sales_data.csv"  # <-- Change this to your file path
df = load_data(file_path)
print(df.head())

# Try parsing any date columns
for col in df.columns:
    if df[col].dtype == object and 'date' in col.lower():
        df[col] = pd.to_datetime(df[col], errors='coerce')

# === Basic Summary ===
summary_stats = df.describe(include='all').transpose()

# === Visualizations ===
chart_paths = []

# Numerical columns: generate histograms
numerical_cols = df.select_dtypes(include=['number']).columns
for col in numerical_cols:
    plt.figure(figsize=(6, 4))
    df[col].dropna().plot(kind='hist', bins=20, color='skyblue', edgecolor='black')
    plt.title(f"Distribution of {col}")
    plt.xlabel(col)
    plt.ylabel("Frequency")
    plt.tight_layout()
    chart_path = f"charts/{col}_distribution.png"
    plt.savefig(chart_path)
    plt.close()
    chart_paths.append((f"Distribution of {col}", chart_path))

# Categorical columns: top 5 frequency bar plots
categorical_cols = df.select_dtypes(include='object').columns
for col in categorical_cols:
    top_categories = df[col].value_counts().nlargest(5)
    if not top_categories.empty:
        plt.figure(figsize=(6, 4))
        top_categories.plot(kind='bar', color='orange')
        plt.title(f"Top Categories in {col}")
        plt.ylabel("Count")
        plt.xticks(rotation=45)
        plt.tight_layout()
        chart_path = f"charts/{col}_top_categories.png"
        plt.savefig(chart_path)
        plt.close()
        chart_paths.append((f"Top Categories in {col}", chart_path))

# === PDF Report ===
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "Data Report", ln=True, align="C")
        self.set_font("Arial", "", 12)
        self.cell(0, 10, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
        self.ln(10)

    def chapter_title(self, title):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, title, ln=True)
        self.ln(5)

    def chapter_body(self, text):
        self.set_font("Arial", "", 11)
        self.multi_cell(0, 10, text)
        self.ln()

    def add_image(self, image_path, w=150):
        self.image(image_path, w=w)
        self.ln()

pdf = PDF()
pdf.add_page()

# === Summary Statistics ===
# === Summary Statistics ===
pdf.chapter_title("Summary Statistics")

# Drop "count" column and recalculate without NaNs
summary_stats_clean = summary_stats.drop("count", axis=1, errors='ignore')
summary_stats_rounded = summary_stats_clean.round(2)

columns = summary_stats_rounded.columns.tolist()
columns_cap = [col.upper() for col in columns]
row_labels = summary_stats_rounded.index.tolist()

# Define dynamic widths
def calculate_col_widths(header_list, total_width=190):
    base_widths = [max(len(str(header)), 8) for header in header_list]
    total_chars = sum(base_widths)
    scale = total_width / total_chars
    return [int(width * scale) for width in base_widths]

headers = ["COLUMN"] + columns_cap
col_widths = calculate_col_widths(headers)

# Header Row
pdf.set_font("Arial", "B", 10)
pdf.set_fill_color(230, 230, 230)

for i, header in enumerate(headers):
    pdf.cell(col_widths[i], 8, header, border=1, align='C', fill=True)
pdf.ln()

# Data Rows
pdf.set_font("Arial", "", 9)
for idx, row in summary_stats_rounded.iterrows():
    pdf.cell(col_widths[0], 8, str(idx)[:20], border=1, align='C')  # Row label
    for i, col in enumerate(columns):
        val = row[col]

        # Leave cell blank if NaN
        if pd.isna(val):
            pdf.cell(col_widths[i + 1], 8, "", border=1, align='C')
            continue

        # Format datetime to DD/MM
        if isinstance(val, pd.Timestamp):
            val = val.strftime("%d/%m")
        elif isinstance(val, str):
            try:
                parsed = pd.to_datetime(val, errors='coerce')
                if pd.notna(parsed):
                    val = parsed.strftime("%d/%m")
            except:
                pass
        elif isinstance(val, float):
            val = f"{val:.2f}"

        val = str(val)[:20]
        pdf.cell(col_widths[i + 1], 8, val, border=1, align='C')
    pdf.ln()
# === Visualizations ===

# Charts
for title, path in chart_paths:
    pdf.add_image(path)

pdf.output("report.pdf")
print("✅ Report Generated: report.pdf")
