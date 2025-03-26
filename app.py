# Import libraries
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# Custom CSS for styling
st.markdown("""
    <style>
    .big-title {
        color: #1E90FF;  /* Dodger Blue for the title */
        font-size: 36px;
        font-weight: bold;
    }
    .secure-text {
        color: #000000;  /* Black for the secure message */
        font-size: 18px;
    }
    </style>
""", unsafe_allow_html=True)

# Function to analyse the sales data
def analyse_sales(data):
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
    loyalty_percentage = (data['Customer_Loyalty'] == 'Yes').mean() * 100
    channel_breakdown = data['Order_Channel'].value_counts()
    avg_shipping = data['Shipping_Cost'].mean()
    return_rate = (data['Return_Status'] == 'Yes').mean() * 100

    st.write("### Sales Analysis Results")
    st.write(f"**Total Sales:** ${total_sales:.2f}")
    st.write(f"**Average Spend per Purchase:** ${avg_spend:.2f}")
    st.write(f"**Number of Unique Customers:** {num_customers}")
    st.write(f"**Average Sales per Customer:** ${sales_per_customer:.2f}")
    st.write(f"**Top Spender:** Customer {top_spender['Customer_ID']} spent ${top_spender['Purchase_Amount']:.2f} on {top_spender['Date']}")
    st.write(f"**Total Items Sold:** {total_quantity}")
    st.write(f"**Most Popular Product Category:** {popular_category}")
    st.write(f"**Payment Method Breakdown:**\n{payment_breakdown.to_string()}")
    st.write(f"**Region with Highest Sales:** {region_sales}")
    st.write(f"**Discount Usage:** {discount_usage['Yes']:.1f}% of purchases had a discount")
    st.write(f"**Average Customer Age:** {avg_age:.1f} years")
    st.write(f"**Gender Breakdown:**\n{gender_breakdown.to_string()}")
    st.write(f"**Loyalty Members:** {loyalty_percentage:.1f}% of customers")
    st.write(f"**Order Channel Breakdown:**\n{channel_breakdown.to_string()}")
    st.write(f"**Average Shipping Cost:** ${avg_shipping:.2f}")
    st.write(f"**Return Rate:** {return_rate:.1f}% of purchases returned")

    chart_type = st.selectbox("Choose a chart to view:", ["Sales by Product Category (Pie)", "Purchases by Payment Method (Bar)"])
    
    data['Date'] = pd.to_datetime(data['Date'])
    if chart_type == "Sales by Product Category (Pie)":
        sales_by_category = data.groupby('Product_Category')['Purchase_Amount'].sum()
        top_5 = sales_by_category.nlargest(5)
        other_sales = sales_by_category.sum() - top_5.sum()
        if other_sales > 0:
            top_5['Other'] = other_sales
        fig, ax = plt.subplots()
        ax.pie(top_5, labels=top_5.index, autopct='%1.1f%%', colors=['#1E90FF', '#87CEEB', '#B0E0E6', '#ADD8E6', '#E0FFFF', '#D3D3D3'])
        ax.set_title('Top 5 Product Categories by Sales (Pie)')
        st.pyplot(fig)
    else:
        fig, ax = plt.subplots()
        payment_breakdown.plot(kind='bar', ax=ax, color='#1E90FF')
        ax.set_title('Purchases by Payment Method')
        ax.set_xlabel('Payment Method')
        ax.set_ylabel('Number of Purchases')
        st.pyplot(fig)

    st.write("### Additional Insights")
    busiest_day = data.groupby('Date')['Purchase_Amount'].sum().idxmax()
    customer_frequency = data['Customer_ID'].value_counts()
    most_frequent_customer = customer_frequency.idxmax()
    avg_items_per_purchase = data['Quantity'].mean()
    top_payment_method = payment_breakdown.idxmax()

    st.write(f"**Busiest Day:** {busiest_day.date()} with ${data.groupby('Date')['Purchase_Amount'].sum().max():.2f} in sales")
    st.write(f"**Most Frequent Customer:** {most_frequent_customer} made {customer_frequency.max()} purchases")
    st.write(f"**Average Items per Purchase:** {avg_items_per_purchase:.2f}")
    st.write(f"**Most Used Payment Method:** {top_payment_method}")

    summary_data = {
        'Metric': [
            'Total Sales', 'Average Spend per Purchase', 'Number of Unique Customers',
            'Average Sales per Customer', 'Total Items Sold', 'Most Popular Product Category',
            'Region with Highest Sales', 'Discount Usage (%)', 'Average Customer Age',
            'Loyalty Members (%)', 'Average Shipping Cost', 'Return Rate (%)', 'Busiest Day',
            'Most Frequent Customer', 'Average Items per Purchase', 'Most Used Payment Method'
        ],
        'Value': [
            f"${total_sales:.2f}", f"${avg_spend:.2f}", num_customers,
            f"${sales_per_customer:.2f}", total_quantity, popular_category,
            region_sales, f"{discount_usage['Yes']:.1f}", f"{avg_age:.1f}",
            f"{loyalty_percentage:.1f}", f"${avg_shipping:.2f}", f"{return_rate:.1f}",
            f"{busiest_day.date()} (${data.groupby('Date')['Purchase_Amount'].sum().max():.2f})",
            f"{most_frequent_customer} ({customer_frequency.max()} purchases)",
            f"{avg_items_per_purchase:.2f}", top_payment_method
        ]
    }
    return pd.DataFrame(summary_data)

# Streamlit app setup
st.sidebar.title("Sales Analyser")
page = st.sidebar.radio("Navigate", ["Welcome", "Analyse Sales"])

if page == "Welcome":
    st.markdown('<p class="big-title">Welcome to Sales Analyser</p>', unsafe_allow_html=True)
    st.markdown('<p class="secure-text">This Is A Secure Algorithm - Unauthorised Access Forbidden.</p>', unsafe_allow_html=True)
else:
    st.markdown('<p class="big-title">Sales Analyser</p>', unsafe_allow_html=True)
    st.write("Upload your CSV file to analyse sales data.")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        try:
            data = pd.read_csv(uploaded_file)
            st.write("File loaded successfully!")
            summary_df = analyse_sales(data)

            csv_buffer = io.StringIO()
            summary_df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="Download Analysis Results",
                data=csv_buffer.getvalue(),
                file_name="sales_analysis_results.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"Error: Something went wrong with the file - {e}")
    else:
        st.info("Please upload a CSV file to start the analysis.")