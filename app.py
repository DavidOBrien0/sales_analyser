# Import libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import openpyxl

# Custom CSS to match the "Code Name Red" design
st.markdown("""
    <style>
    /* Import Montserrat font from Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');

    /* Global styles */
    html, body, [class*="css"] {
        font-family: 'Montserrat', 'Courier New', Courier, monospace !important;
        background-color: #000000; /* Black background */
        color: #FFFFFF; /* White text */
    }

    /* Main container */
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 40px 20px;
        text-align: center;
    }

    /* Header (Navigation Bar) */
    .header {
        background-color: #000000;
        padding: 15px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #FFFFFF;
    }
    .header-logo {
        font-size: 16px;
        font-weight: 700;
        text-transform: uppercase;
        color: #FFFFFF;
    }
    .header-nav a {
        color: #FFFFFF;
        font-size: 14px;
        font-weight: 700;
        text-transform: uppercase;
        margin: 0 15px;
        text-decoration: none;
        transition: color 0.3s ease;
    }
    .header-nav a:hover {
        color: #00FF00; /* Matrix green on hover */
    }

    /* Sidebar styling */
    .css-1d391kg { /* Streamlit sidebar class */
        background-color: #000000;
        padding: 20px;
        border-right: 1px solid #FFFFFF;
    }
    .css-1d391kg .stRadio > label {
        color: #FFFFFF;
        font-size: 14px;
        font-weight: 700;
        text-transform: uppercase;
        padding: 10px;
        transition: color 0.3s ease;
    }
    .css-1d391kg .stRadio > label:hover {
        color: #00FF00; /* Matrix green on hover */
    }
    .css-1d391kg .stSidebar > div > div > div > div > h1 {
        color: #FFFFFF;
        font-size: 18px;
        font-weight: 700;
        text-transform: uppercase;
    }

    /* Homepage styling */
    .big-title {
        font-size: 72px;
        font-weight: 700;
        color: #FFFFFF;
        text-transform: uppercase;
        line-height: 1.2;
        margin-bottom: 20px;
    }
    .secure-text {
        font-size: 16px;
        color: #FFFFFF;
        margin-bottom: 30px;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }
    .stTextInput > div > input {
        background-color: #000000;
        color: #FFFFFF;
        border: 1px solid #FFFFFF;
        border-radius: 0;
        padding: 10px;
        font-size: 14px;
        text-transform: uppercase;
        transition: border-color 0.3s ease;
    }
    .stTextInput > div > input:focus {
        border-color: #00FF00; /* Matrix green */
    }

    /* Button styling */
    .stButton>button {
        background-color: #000000;
        color: #FFFFFF;
        border: 1px solid #FFFFFF;
        border-radius: 0;
        padding: 10px 20px;
        font-size: 14px;
        font-weight: 700;
        text-transform: uppercase;
        transition: background-color 0.3s ease, color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #FFFFFF;
        color: #000000;
    }

    /* Analysis page styling */
    .analysis-section {
        padding: 20px;
        text-align: left;
    }
    .analysis-section h3 {
        color: #FFFFFF;
        font-size: 24px;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 15px;
    }
    .analysis-section p, .analysis-section div {
        font-size: 14px;
        line-height: 1.6;
    }

    /* File uploader styling */
    .stFileUploader > div > div {
        background-color: #000000;
        border: 1px solid #FFFFFF;
        border-radius: 0;
        padding: 20px;
        text-align: center;
        transition: border-color 0.3s ease;
    }
    .stFileUploader > div > div:hover {
        border-color: #00FF00; /* Matrix green */
    }

    /* Selectbox styling */
    .stSelectbox > div > div {
        background-color: #000000;
        color: #FFFFFF;
        border: 1px solid #FFFFFF;
        border-radius: 0;
        padding: 8px;
    }
    .stSelectbox > div > div > select {
        color: #FFFFFF;
        text-transform: uppercase;
    }

    /* Download buttons */
    .stDownloadButton > button {
        background-color: #000000;
        color: #FFFFFF;
        border: 1px solid #FFFFFF;
        border-radius: 0;
        padding: 10px 20px;
        font-size: 14px;
        font-weight: 700;
        text-transform: uppercase;
        margin: 5px;
        transition: background-color 0.3s ease, color 0.3s ease;
    }
    .stDownloadButton > button:hover {
        background-color: #FFFFFF;
        color: #000000;
    }

    /* Plotly chart container */
    .plotly-chart-container {
        background: #000000;
        padding: 15px;
        border: 1px solid #FFFFFF;
        margin-top: 20px;
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
    try:
        data['Day_Month'] = data['Day_Month'].astype(str)
        data['Year'] = data['Year'].astype(str)
        data['Full_Date'] = pd.to_datetime(data['Day_Month'] + '/' + data['Year'], format='%d/%m/%Y', errors='coerce')
        if data['Full_Date'].isnull().all():
            st.error("DATE COLUMN ISSUE: All 'Day_Month/Year' values are invalid—check your CSV format.")
            return None
    except KeyError as e:
        st.error(f"DATE COLUMN ISSUE: Missing 'Day_Month' or 'Year' column - {e}")
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
    popular_age = data['Product_Category'].mode()[0]
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
    st.write(f"**MOST POPULAR AGE:** {popular_age}")
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

    st.write("### VISUALISE YOUR DATA")
    chart_options = [
        "SALES OVER TIME (LINE)", 
        "PURCHASES BY PAYMENT METHOD (BAR)", 
        "SALES BY REGION (BAR)", 
        "SALES BY AGE (PIE)", 
        "DISCOUNT USAGE (PIE)", 
        "PURCHASE AMOUNT VS CUSTOMER AGE (SCATTER)", 
        "CUSTOMER AGE DISTRIBUTION (HISTOGRAM)",
        "SALES BY LOYALTY STATUS (SUNBURST)",
        "BUILD YOUR OWN CHART"
    ]
    chart_type = st.selectbox("CHOOSE A CHART TO VIEW:", chart_options)

    plot_layout = dict(
        plot_bgcolor='#000000',
        paper_bgcolor='#000000',
        font=dict(family="Courier New, monospace", color="#FFFFFF"),
        title_font=dict(size=20, color="#FFFFFF"),
        xaxis=dict(gridcolor="#FFFFFF", zerolinecolor="#FFFFFF"),
        yaxis=dict(gridcolor="#FFFFFF", zerolinecolor="#FFFFFF"),
        hoverlabel=dict(bgcolor="#FFFFFF", font=dict(color="#000000")),
    )

    if chart_type == "SALES OVER TIME (LINE)":
        sales_by_date = data.groupby('Full_Date')['Purchase_Amount'].sum().reset_index()
        fig = px.line(
            sales_by_date, 
            x='Full_Date', 
            y='Purchase_Amount',
            title='SALES OVER TIME',
            labels={'Full_Date': 'DATE (DD/MM)', 'Purchase_Amount': 'TOTAL SALES ($)'},
            line_shape='spline',
            color_discrete_sequence=['#FFFFFF']
        )
        fig.update_layout(**plot_layout)
        fig.update_traces(line=dict(width=3), hovertemplate='Date: %{x|%d/%m}<br>Sales: $%{y:.2f}')
        st.markdown('<div class="plotly-chart-container">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    elif chart_type == "PURCHASES BY PAYMENT METHOD (BAR)":
        fig = px.bar(
            payment_breakdown.reset_index(),
            x='Payment_Method',
            y='count',
            title='PURCHASES BY PAYMENT METHOD',
            labels={'Payment_Method': 'PAYMENT METHOD', 'count': 'NUMBER OF PURCHASES'},
            color='Payment_Method',
            color_discrete_sequence=px.colors.sequential.Greys
        )
        fig.update_layout(**plot_layout, showlegend=False)
        fig.update_traces(hovertemplate='Method: %{x}<br>Count: %{y}')
        st.markdown('<div class="plotly-chart-container">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    elif chart_type == "SALES BY REGION (BAR)":
        sales_by_region = data.groupby('Region')['Purchase_Amount'].sum().reset_index()
        fig = px.bar(
            sales_by_region,
            x='Region',
            y='Purchase_Amount',
            title='SALES BY REGION',
            labels={'Region': 'REGION', 'Purchase_Amount': 'TOTAL SALES ($)'},
            color='Region',
            color_discrete_sequence=px.colors.sequential.Greys
        )
        fig.update_layout(**plot_layout, showlegend=False)
        fig.update_traces(hovertemplate='Region: %{x}<br>Sales: $%{y:.2f}')
        st.markdown('<div class="plotly-chart-container">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    elif chart_type == "SALES BY AGE (PIE)":
        sales_by_category = data.groupby('Product_Category')['Purchase_Amount'].sum().reset_index()
        top_5 = sales_by_category.nlargest(5, 'Purchase_Amount')
        other_sales = sales_by_category['Purchase_Amount'].sum() - top_5['Purchase_Amount'].sum()
        if other_sales > 0:
            top_5 = pd.concat([top_5, pd.DataFrame({'Product_Category': ['Other'], 'Purchase_Amount': [other_sales]})], ignore_index=True)
        fig = px.pie(
            top_5,
            names='Product_Category',
            values='Purchase_Amount',
            title='TOP 5 AGES BY SALES (PIE)',
            color_discrete_sequence=px.colors.sequential.Greys
        )
        fig.update_layout(**plot_layout)
        fig.update_traces(textinfo='percent+label', hovertemplate='Age: %{label}<br>Sales: $%{value:.2f}')
        st.markdown('<div class="plotly-chart-container">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    elif chart_type == "DISCOUNT USAGE (PIE)":
        discount_counts = data['Discount_Applied'].value_counts().reset_index()
        fig = px.pie(
            discount_counts,
            names='Discount_Applied',
            values='count',
            title='DISCOUNT USAGE',
            color_discrete_sequence=['#FFFFFF', '#666666']
        )
        fig.update_layout(**plot_layout)
        fig.update_traces(textinfo='percent+label', hovertemplate='Discount: %{label}<br>Count: %{value}')
        st.markdown('<div class="plotly-chart-container">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    elif chart_type == "PURCHASE AMOUNT VS CUSTOMER AGE (SCATTER)":
        fig = px.scatter(
            data,
            x='Customer_Age',
            y='Purchase_Amount',
            title='PURCHASE AMOUNT VS CUSTOMER AGE',
            labels={'Customer_Age': 'CUSTOMER AGE', 'Purchase_Amount': 'PURCHASE AMOUNT ($)'},
            color='Customer_Gender',
            size='Quantity',
            color_discrete_sequence=['#FFFFFF', '#666666'],
            opacity=0.7
        )
        fig.update_layout(**plot_layout)
        fig.update_traces(hovertemplate='Age: %{x}<br>Amount: $%{y:.2f}<br>Gender: %{marker.color}')
        st.markdown('<div class="plotly-chart-container">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    elif chart_type == "CUSTOMER AGE DISTRIBUTION (HISTOGRAM)":
        fig = px.histogram(
            data,
            x='Customer_Age',
            title='CUSTOMER AGE DISTRIBUTION',
            labels={'Customer_Age': 'AGE', 'count': 'NUMBER OF CUSTOMERS'},
            color_discrete_sequence=['#FFFFFF'],
            nbins=10
        )
        fig.update_layout(**plot_layout)
        fig.update_traces(hovertemplate='Age Range: %{x}<br>Count: %{y}')
        st.markdown('<div class="plotly-chart-container">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    elif chart_type == "SALES BY LOYALTY STATUS (SUNBURST)":
        sunburst_data = data.groupby(['Customer_Loyalty', 'Region'])['Purchase_Amount'].sum().reset_index()
        fig = px.sunburst(
            sunburst_data,
            path=['Customer_Loyalty', 'Region'],
            values='Purchase_Amount',
            title='SALES BY LOYALTY STATUS AND REGION (SUNBURST)',
            color='Purchase_Amount',
            color_continuous_scale='Greys'
        )
        fig.update_layout(**plot_layout)
        fig.update_traces(hovertemplate='Loyalty: %{parent}<br>Region: %{label}<br>Sales: $%{value:.2f}')
        st.markdown('<div class="plotly-chart-container">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    elif chart_type == "BUILD YOUR OWN CHART":
        numeric_cols = data.select_dtypes(include=['int64', 'float64']).columns.tolist()
        x_axis = st.selectbox("CHOOSE X-AXIS:", data.columns.tolist())
        y_axis = st.selectbox("CHOOSE Y-AXIS (FOR SCATTER/BAR/LINE):", ["None"] + numeric_cols)
        custom_chart_type = st.selectbox("CHOOSE CHART TYPE:", ["BAR", "LINE", "PIE", "SCATTER", "HISTOGRAM"])
        color_by = st.selectbox("COLOR BY (OPTIONAL):", ["None"] + data.columns.tolist())

        if custom_chart_type == "BAR" and y_axis != "None":
            fig = px.bar(
                data,
                x=x_axis,
                y=y_axis,
                color=color_by if color_by != "None" else None,
                title=f"{y_axis} BY {x_axis} (BAR)",
                color_discrete_sequence=px.colors.sequential.Greys
            )
        elif custom_chart_type == "LINE" and y_axis != "None":
            fig = px.line(
                data,
                x=x_axis,
                y=y_axis,
                color=color_by if color_by != "None" else None,
                title=f"{y_axis} BY {x_axis} (LINE)",
                line_shape='spline',
                color_discrete_sequence=px.colors.sequential.Greys
            )
        elif custom_chart_type == "PIE":
            pie_data = data.groupby(x_axis)[y_axis].sum().reset_index() if y_axis != "None" else data[x_axis].value_counts().reset_index()
            fig = px.pie(
                pie_data,
                names=x_axis,
                values=y_axis if y_axis != "None" else 'count',
                title=f"{x_axis} BREAKDOWN (PIE)",
                color_discrete_sequence=px.colors.sequential.Greys
            )
        elif custom_chart_type == "SCATTER" and y_axis != "None":
            fig = px.scatter(
                data,
                x=x_axis,
                y=y_axis,
                color=color_by if color_by != "None" else None,
                title=f"{y_axis} VS {x_axis} (SCATTER)",
                color_discrete_sequence=px.colors.sequential.Greys
            )
        elif custom_chart_type == "HISTOGRAM":
            fig = px.histogram(
                data,
                x=x_axis,
                color=color_by if color_by != "None" else None,
                title=f"{x_axis} DISTRIBUTION (HISTOGRAM)",
                color_discrete_sequence=px.colors.sequential.Greys
            )
        else:
            st.write("Please select valid options to build your chart.")
            return pd.DataFrame(summary_data)

        fig.update_layout(**plot_layout)
        st.markdown('<div class="plotly-chart-container">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

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
            'AVERAGE SALES PER CUSTOMER', 'TOTAL BOOKS SOLD', 'MOST POPULAR AGE',
            'REGION WITH HIGHEST SALES', 'DISCOUNT USAGE (%)', 'AVERAGE CUSTOMER AGE',
            'NUMBER OF ORDERS', 'AVERAGE SHIPPING COST', 'TOTAL TAX PAID', 'NUMBER OF UNIQUE TITLES',
            'AVERAGE UNIT PRICE', 'RETURN RATE (%)', 'LOYALTY MEMBERS (%)', 'AVERAGE CUSTOMER RATING',
            'BUSIEST DAY', 'MOST FREQUENT CUSTOMER', 'AVERAGE BOOKS PER PURCHASE', 'MOST USED PAYMENT METHOD'
        ],
        'VALUE': [
            f"${total_sales:.2f}", f"${avg_spend:.2f}", num_customers,
            f"${sales_per_customer:.2f}", total_quantity, str(popular_age),
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
# Custom header (replacing sidebar title)
st.markdown("""
    <div class="header">
        <div class="header-logo">BOOKSTORE ANALYTICS</div>
        <div class="header-nav">
            <a href="#">HOME</a>
            <a href="#">ANALYSE SALES</a>
        </div>
    </div>
""", unsafe_allow_html=True)

# Sidebar for navigation
page = st.sidebar.radio("NAVIGATE", ["HOME", "ANALYSE SALES"])

# Use session state to track if password is correct
if 'password_correct' not in st.session_state:
    st.session_state.password_correct = False

# Main content container
with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    if page == "HOME":
        st.markdown('<p class="big-title">BOOKSTORE SALES ANALYSER</p>', unsafe_allow_html=True)
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
                with st.container():
                    st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
                    summary_df = analyse_sales(data)
                    if summary_df is not None:
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
                    st.markdown('</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"ERROR: SOMETHING WENT WRONG WITH THE FILE - {e}")
        else:
            st.info("PLEASE UPLOAD A CSV FILE TO START THE ANALYSIS.")
    else:
        st.markdown('<p class="big-title">BOOKSTORE SALES ANALYSER</p>', unsafe_allow_html=True)
        st.warning("PLEASE ENTER THE CORRECT PASSWORD ON THE HOME PAGE TO ACCESS THIS SECTION.")

    st.markdown('</div>', unsafe_allow_html=True)