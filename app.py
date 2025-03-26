# Import libraries
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# Function to analyse the sales data
def analyse_sales(data):
    # Detailed summary
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

    # Display summaries
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

    # Chart selection
    chart_type = st.selectbox("Choose a chart to view:", ["Sales by Product Category (Pie)", "Purchases by Payment Method (Bar)"])
    
    data['Date'] = pd.to_datetime(data['Date'])
    if chart_type == "Sales by Product Category (Pie)":
        sales_by_category = data.groupby('Product_Category')['Purchase_Amount'].sum()
        fig, ax = plt.subplots()
        ax.pie(sales_by_category, labels=sales_by_category.index, autopct='%1.1f%%')
        ax.set_title('Sales Distribution by Product Category')
        st.pyplot(fig)
    else:  # Purchases by Payment Method (Bar)
        fig, ax = plt.subplots()
        payment_breakdown.plot(kind='bar', ax=ax)
        ax.set_title('Purchases by Payment Method')
        ax.set_xlabel('Payment Method')
        ax.set_ylabel('Number of Purchases')
        st.pyplot(fig)

    # Additional insights
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

    # Prepare summary data for download
    summary_data = {
        'Metric': [
            'Total Sales', 'Average Spend per Purchase', 'Number of Unique Customers',
            'Average Sales per Customer', 'Total Items Sold', 'Most Popular Product Category',
            'Region with Highest Sales', 'Discount Usage (%)', 'Busiest Day', 'Most Frequent Customer',
            'Average Items per Purchase', 'Most Used Payment Method'
        ],
        'Value': [
            f"${total_sales:.2f}", f"${avg_spend:.2f}", num_customers,
            f"${sales_per_customer:.2f}", total_quantity, popular_category,
            region_sales, f"{discount_usage['Yes']:.1f}", 
            f"{busiest_day.date()} (${data.groupby('Date')['Purchase_Amount'].sum().max():.2f})",
            f"{most_frequent_customer} ({customer_frequency.max()} purchases)",
            f"{avg_items_per_purchase:.2f}", top_payment_method
        ]
    }
    return pd.DataFrame(summary_data)

# Streamlit app setup with welcome page
st.sidebar.title("Sales Analyser")
page = st.sidebar.radio("Navigate", ["Welcome", "Analyse Sales"])

if page == "Welcome":
    st.title("Welcome to Sales Analyser")
    st.write("Built by David - the grandest analyser in town!")
    st.write("This app lets you upload a CSV file to analyse your sales data, view charts, and download results.")
    st.write("Head to 'Analyse Sales' on the left to get started!")
else:  # Analyse Sales page
    st.title("Sales Analyser")
    st.write("Upload your CSV file to analyse sales data.")

    # File uploader
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        try:
            # Read the uploaded file
            data = pd.read_csv(uploaded_file)
            st.write("File loaded successfully!")
            
            # Run analysis and get summary for download
            summary_df = analyse_sales(data)

            # Download button
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

