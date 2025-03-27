# Import libraries
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import openpyxl

# Custom CSS for styling
st.markdown("""
    <style>
    /* Apply Matrix-style font to all text */
    * {
        font-family: 'Courier New', Courier, monospace !important;
    }
    .big-title {
        color: #1E90FF;
        font-size: 36px;
        font-weight: bold;
    }
    .secure-text {
        color: #000000;
        font-size: 18px;
    }
    </style>
""", unsafe_allow_html=True)

# Define the correct password
correct_password = "Letmein"

# Function to generate PDF
def generate_pdf(summary_df, filename="bookstore_sales_analysis.pdf"):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Courier", 12)
    y = 750
    for index, row in summary_df.iterrows():
        text = f"{row['METRIC']}: {row['VALUE']}"
        c.drawString(50, y, text)
        y -= 20
        if y < 50:
            c.showPage()
            y = 750
    c.save()
    buffer.seek(0)
    return buffer

# Function to analyse the sales data
def analyse_sales(data):
    # Combine Day_Month and Year into a full datetime
    try:
        data['Full_Date'] = pd.to_datetime(data['Day_Month'] + '/' + data['Year'], format='%d/%m/%Y', errors='coerce')
        if data['Full_Date'].isnull().all():
            st.error("DATE COLUMN ISSUE: All 'Day_Month/Year' values are invalid—check your CSV format.")
            return None
    except Exception as e:
        st.error(f"DATE COLUMN ISSUE: {e}")
        return None

    total_sales = data['Purchase_Amount'].sum()
    avg_spend = data['Purchase_Amount'].mean()
    num_customers = data['Customer_ID'].nunique()
    sales_per_customer = total_sales / num_customers
    top_spender = data.loc[data['Purchase_Amount'].idxmax()]
    total_quantity = data['Quantity'].sum()
    popular_category = data['Product_Category'].mode()[0]
    payment_breakdown = data['Payment_Method'].value_counts()
    region_sales = data.groupby('Region')['Purchase_Amount'].sum().idxmax()
    discount_usage = data['Discount_Applied'].value_counts(normalize=True) * 100
    avg_age = data['Customer_Age'].mean()
    gender_breakdown = data['Customer_Gender'].value_counts()
    num_orders = data['Order_ID'].nunique()
    time_breakdown = data['Transaction_Time'].value_counts()
    avg_shipping = data['Shipping_Cost'].mean()
    total_tax = data['Tax_Amount'].sum()
    num_products = data['Product_ID'].nunique()
    avg_unit_price = data['Unit_Price'].mean()
    return_rate = (data['Return_Status'] == 'Yes').mean() * 100
    loyalty_percentage = (data['Customer_Loyalty'] == 'Yes').mean() * 100
    channel_breakdown = data['Order_Channel'].value_counts()
    delivery_breakdown = data['Delivery_Method'].value_counts()
    avg_rating = data['Customer_Rating'].mean()
    source_breakdown = data['Purchase_Source'].value_counts()

    # Insights Engine
    st.write("### KEY INSIGHTS")
    sales_by_date = data.groupby('Full_Date')['Purchase_Amount'].sum()
    max_spike_date = sales_by_date.idxmax()
    max_spike_value = sales_by_date.max()
    avg_sales = sales_by_date.mean()
    if pd.notnull(max_spike_date) and max_spike_value > avg_sales * 1.2:
        spike_percent = ((max_spike_value - avg_sales) / avg_sales) * 100
        st.write(f"**BIGGEST SALES SPIKE:** {max_spike_date.strftime('%d/%m')} - ${max_spike_value:.2f} (UP {spike_percent:.1f}% FROM AVERAGE!)")
    outlier_spend = data['Purchase_Amount'].quantile(0.95)
    if top_spender['Purchase_Amount'] > outlier_spend:
        st.write(f"**OUTLIER ALERT:** Customer {top_spender['Customer_ID']} spent ${top_spender['Purchase_Amount']:.2f} - TOP 5%!")

    st.write("### SALES ANALYSIS RESULTS")
    st.write(f"**TOTAL SALES:** ${total_sales:.2f}")
    st.write(f"**AVERAGE SPEND PER PURCHASE:** ${avg_spend:.2f}")
    st.write(f"**NUMBER OF UNIQUE CUSTOMERS:** {num_customers}")
    st.write(f"**AVERAGE SALES PER CUSTOMER:** ${sales_per_customer:.2f}")
    st.write(f"**TOP SPENDER:** Customer {top_spender['Customer_ID']} spent ${top_spender['Purchase_Amount']:.2f} on {top_spender['Day_Month']}")
    st.write(f"**TOTAL BOOKS SOLD:** {total_quantity}")
    st.write(f"**MOST POPULAR GENRE:** {popular_category}")
    st.write(f"**PAYMENT METHOD BREAKDOWN:**\n{payment_breakdown.to_string()}")
    st.write(f"**REGION WITH HIGHEST SALES:** {region_sales}")
    st.write(f"**DISCOUNT USAGE:** {discount_usage.get('Yes', 0):.1f}% of purchases had a discount")
    st.write(f"**AVERAGE CUSTOMER AGE:** {avg_age:.1f} years")
    st.write(f"**GENDER BREAKDOWN:**\n{gender_breakdown.to_string()}")
    st.write(f"**NUMBER OF ORDERS:** {num_orders}")
    st.write(f"**TRANSACTION TIME BREAKDOWN:**\n{time_breakdown.to_string()}")
    st.write(f"**AVERAGE SHIPPING COST:** ${avg_shipping:.2f}")
    st.write(f"**TOTAL TAX PAID:** ${total_tax:.2f}")
    st.write(f"**NUMBER OF UNIQUE TITLES:** {num_products}")
    st.write(f"**AVERAGE UNIT PRICE:** ${avg_unit_price:.2f}")
    st.write(f"**RETURN RATE:** {return_rate:.1f}% of purchases returned")
    st.write(f"**LOYALTY MEMBERS:** {loyalty_percentage:.1f}% of customers")
    st.write(f"**ORDER CHANNEL BREAKDOWN:**\n{channel_breakdown.to_string()}")
    st.write(f"**DELIVERY METHOD BREAKDOWN:**\n{delivery_breakdown.to_string()}")
    st.write(f"**AVERAGE CUSTOMER RATING:** {avg_rating:.1f}/5")
    st.write(f"**PURCHASE SOURCE BREAKDOWN:**\n{source_breakdown.to_string()}")

    # Chart Section
    st.write("### VISUALISE YOUR DATA")
    chart_options = [
        "SALES OVER TIME (LINE)", 
        "PURCHASES BY PAYMENT METHOD (BAR)", 
        "SALES BY REGION (BAR)", 
        "SALES BY GENRE (PIE)", 
        "DISCOUNT USAGE (PIE)", 
        "PURCHASE AMOUNT VS CUSTOMER AGE (SCATTER)", 
        "CUSTOMER AGE DISTRIBUTION (HISTOGRAM)",
        "BUILD YOUR OWN CHART"
    ]
    chart_type = st.selectbox("CHOOSE A CHART TO VIEW:", chart_options)
    
    if chart_type == "SALES OVER TIME (LINE)":
        sales_by_date = data.groupby('Full_Date')['Purchase_Amount'].sum()
        fig, ax = plt.subplots()
        ax.plot(sales_by_date.index, sales_by_date.values, color='#1E90FF')
        ax.set_title('SALES OVER TIME')
        ax.set_xlabel('DATE (DD/MM)')
        ax.set_ylabel('TOTAL SALES ($)')
        plt.xticks(rotation=45)
        st.pyplot(fig)
    elif chart_type == "PURCHASES BY PAYMENT METHOD (BAR)":
        fig, ax = plt.subplots()
        payment_breakdown.plot(kind='bar', ax=ax, color='#1E90FF')
        ax.set_title('PURCHASES BY PAYMENT METHOD')
        ax.set_xlabel('PAYMENT METHOD')
        ax.set_ylabel('NUMBER OF PURCHASES')
        st.pyplot(fig)
    elif chart_type == "SALES BY REGION (BAR)":
        sales_by_region = data.groupby('Region')['Purchase_Amount'].sum()
        fig, ax = plt.subplots()
        sales_by_region.plot(kind='bar', ax=ax, color='#1E90FF')
        ax.set_title('SALES BY REGION')
        ax.set_xlabel('REGION')
        ax.set_ylabel('TOTAL SALES ($)')
        st.pyplot(fig)
    elif chart_type == "SALES BY GENRE (PIE)":
        sales_by_category = data.groupby('Product_Category')['Purchase_Amount'].sum()
        top_5 = sales_by_category.nlargest(5)
        other_sales = sales_by_category.sum() - top_5.sum()
        if other_sales > 0:
            top_5['Other'] = other_sales
        fig, ax = plt.subplots()
        ax.pie(top_5, labels=top_5.index, autopct='%1.1f%%', colors=['#1E90FF', '#87CEEB', '#B0E0E6', '#ADD8E6', '#E0FFFF', '#D3D3D3'])
        ax.set_title('TOP 5 GENRES BY SALES (PIE)')
        st.pyplot(fig)
    elif chart_type == "DISCOUNT USAGE (PIE)":
        fig, ax = plt.subplots()
        discount_counts = data['Discount_Applied'].value_counts()
        ax.pie(discount_counts, labels=discount_counts.index, autopct='%1.1f%%', colors=['#1E90FF', '#87CEEB'])
        ax.set_title('DISCOUNT USAGE')
        st.pyplot(fig)
    elif chart_type == "PURCHASE AMOUNT VS CUSTOMER AGE (SCATTER)":
        fig, ax = plt.subplots()
        ax.scatter(data['Customer_Age'], data['Purchase_Amount'], color='#1E90FF', alpha=0.5)
        ax.set_title('PURCHASE AMOUNT VS CUSTOMER AGE')
        ax.set_xlabel('CUSTOMER AGE')
        ax.set_ylabel('PURCHASE AMOUNT ($)')
        st.pyplot(fig)
    elif chart_type == "CUSTOMER AGE DISTRIBUTION (HISTOGRAM)":
        fig, ax = plt.subplots()
        ax.hist(data['Customer_Age'], bins=10, color='#1E90FF', edgecolor='black')
        ax.set_title('CUSTOMER AGE DISTRIBUTION')
        ax.set_xlabel('AGE')
        ax.set_ylabel('NUMBER OF CUSTOMERS')
        st.pyplot(fig)
    elif chart_type == "BUILD YOUR OWN CHART":
        numeric_cols = data.select_dtypes(include=['int64', 'float64']).columns.tolist()
        x_axis = st.selectbox("CHOOSE X-AXIS:", numeric_cols + data.columns.tolist())
        y_axis = st.selectbox("CHOOSE Y-AXIS (FOR SCATTER/BAR/LINE):", ["None"] + numeric_cols)
        custom_chart_type = st.selectbox("CHOOSE CHART TYPE:", ["BAR", "LINE", "PIE", "SCATTER", "HISTOGRAM"])
        
        fig, ax = plt.subplots()
        if custom_chart_type == "BAR" and y_axis != "None":
            data.groupby(x_axis)[y_axis].sum().plot(kind='bar', ax=ax, color='#1E90FF')
            ax.set_title(f"{y_axis} BY {x_axis} (BAR)")
        elif custom_chart_type == "LINE" and y_axis != "None":
            data.groupby(x_axis)[y_axis].sum().plot(kind='line', ax=ax, color='#1E90FF')
            ax.set_title(f"{y_axis} BY {x_axis} (LINE)")
        elif custom_chart_type == "PIE":
            data[x_axis].value_counts().plot(kind='pie', ax=ax, autopct='%1.1f%%', colors=['#1E90FF', '#87CEEB', '#B0E0E6'])
            ax.set_title(f"{x_axis} BREAKDOWN (PIE)")
        elif custom_chart_type == "SCATTER" and y_axis != "None":
            ax.scatter(data[x_axis], data[y_axis], color='#1E90FF', alpha=0.5)
            ax.set_title(f"{y_axis} VS {x_axis} (SCATTER)")
        elif custom_chart_type == "HISTOGRAM":
            ax.hist(data[x_axis], bins=10, color='#1E90FF', edgecolor='black')
            ax.set_title(f"{x_axis} DISTRIBUTION (HISTOGRAM)")
        ax.set_xlabel(x_axis.upper())
        if y_axis != "None":
            ax.set_ylabel(y_axis.upper())
        plt.xticks(rotation=45)
        st.pyplot(fig)

    st.write("### ADDITIONAL INSIGHTS")
    busiest_day = data.groupby('Full_Date')['Purchase_Amount'].sum().idxmax()
    customer_frequency = data['Customer_ID'].value_counts()
    most_frequent_customer = customer_frequency.idxmax()
    avg_items_per_purchase = data['Quantity'].mean()
    top_payment_method = payment_breakdown.idxmax()

    st.write(f"**BUSIEST DAY:** {busiest_day.strftime('%d/%m')} with ${data.groupby('Full_Date')['Purchase_Amount'].sum().max():.2f} in sales")
    st.write(f"**MOST FREQUENT CUSTOMER:** {most_frequent_customer} made {customer_frequency.max()} purchases")
    st.write(f"**AVERAGE BOOKS PER PURCHASE:** {avg_items_per_purchase:.2f}")
    st.write(f"**MOST USED PAYMENT METHOD:** {top_payment_method}")

    summary_data = {
        'METRIC': [
            'TOTAL SALES', 'AVERAGE SPEND PER PURCHASE', 'NUMBER OF UNIQUE CUSTOMERS',
            'AVERAGE SALES PER CUSTOMER', 'TOTAL BOOKS SOLD', 'MOST POPULAR GENRE',
            'REGION WITH HIGHEST SALES', 'DISCOUNT USAGE (%)', 'AVERAGE CUSTOMER AGE',
            'NUMBER OF ORDERS', 'AVERAGE SHIPPING COST', 'TOTAL TAX PAID', 'NUMBER OF UNIQUE TITLES',
            'AVERAGE UNIT PRICE', 'RETURN RATE (%)', 'LOYALTY MEMBERS (%)', 'AVERAGE CUSTOMER RATING',
            'BUSIEST DAY', 'MOST FREQUENT CUSTOMER', 'AVERAGE BOOKS PER PURCHASE', 'MOST USED PAYMENT METHOD'
        ],
        'VALUE': [
            f"${total_sales:.2f}", f"${avg_spend:.2f}", num_customers,
            f"${sales_per_customer:.2f}", total_quantity, popular_category,
            region_sales, f"{discount_usage.get('Yes', 0):.1f}", f"{avg_age:.1f}",
            num_orders, f"${avg_shipping:.2f}", f"${total_tax:.2f}", num_products,
            f"${avg_unit_price:.2f}", f"{return_rate:.1f}", f"{loyalty_percentage:.1f}",
            f"{avg_rating:.1f}", busiest_day.strftime('%d/%m') + f" (${data.groupby('Full_Date')['Purchase_Amount'].sum().max():.2f})",
            f"{most_frequent_customer} ({customer_frequency.max()} purchases)",
            f"{avg_items_per_purchase:.2f}", top_payment_method
        ]
    }
    return pd.DataFrame(summary_data)

# Streamlit app setup
st.sidebar.title("BOOKSTORE SALES ANALYSER")
page = st.sidebar.radio("NAVIGATE", ["HOME", "ANALYSE SALES"])

# Use session state to track if password is correct
if 'password_correct' not in st.session_state:
    st.session_state.password_correct = False

if page == "HOME":
    st.markdown('<p class="big-title">WELCOME TO BOOKSTORE SALES ANALYSER</p>', unsafe_allow_html=True)
    st.markdown('<p class="secure-text">THIS IS A SECURE ALGORITHM - UNAUTHORISED ACCESS IS FORBIDDEN.</p>', unsafe_allow_html=True)
    
    password = st.text_input("ENTER PASSWORD TO ACCESS ANALYSIS:", type="password")
    if st.button("SUBMIT"):
        if password == correct_password:
            st.session_state.password_correct = True
            st.success("PASSWORD ACCEPTED! YOU CAN NOW SWITCH TO 'ANALYSE SALES'.")
        else:
            st.error("INCORRECT PASSWORD. TRY AGAIN.")

elif page == "ANALYSE SALES" and st.session_state.password_correct:
    st.markdown('<p class="big-title">BOOKSTORE SALES ANALYSER</p>', unsafe_allow_html=True)
    st.write("UPLOAD YOUR CSV FILE TO ANALYSE BOOKSTORE SALES DATA.")

    uploaded_file = st.file_uploader("CHOOSE A CSV FILE", type="csv")

    if uploaded_file is not None:
        try:
            data = pd.read_csv(uploaded_file)
            st.write("FILE LOADED SUCCESSFULLY!")
            summary_df = analyse_sales(data)
            if summary_df is not None:
                # Export Options
                st.write("### DOWNLOAD YOUR RESULTS")
                col1, col2, col3 = st.columns(3)
                with col1:
                    csv_buffer = io.StringIO()
                    summary_df.to_csv(csv_buffer, index=False)
                    st.download_button(
                        label="DOWNLOAD CSV",
                        data=csv_buffer.getvalue(),
                        file_name="bookstore_sales_analysis.csv",
                        mime="text/csv"
                    )
                with col2:
                    pdf_buffer = generate_pdf(summary_df)
                    st.download_button(
                        label="DOWNLOAD PDF",
                        data=pdf_buffer,
                        file_name="bookstore_sales_analysis.pdf",
                        mime="application/pdf"
                    )
                with col3:
                    excel_buffer = io.BytesIO()
                    summary_df.to_excel(excel_buffer, index=False, engine='openpyxl')
                    excel_buffer.seek(0)
                    st.download_button(
                        label="DOWNLOAD EXCEL",
                        data=excel_buffer,
                        file_name="bookstore_sales_analysis.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        except Exception as e:
            st.error(f"ERROR: SOMETHING WENT WRONG WITH THE FILE - {e}")
    else:
        st.info("PLEASE UPLOAD A CSV FILE TO START THE ANALYSIS.")
else:
    st.markdown('<p class="big-title">BOOKSTORE SALES ANALYSER</p>', unsafe_allow_html=True)
    st.warning("PLEASE ENTER THE CORRECT PASSWORD ON THE HOME PAGE TO ACCESS THIS SECTION.")