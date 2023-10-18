import pandas as pd
import streamlit as st 
import plotly.graph_objects as go

from PIL import Image
 
st.set_page_config(page_title="Sales Dashboard", page_icon=":bar_chart:", layout="wide")

@st.cache
def get_data(path:str) -> pd.DataFrame:
    data_frame = pd.read_csv(
        path,
    )
    return data_frame

@st.cache
def get_image(path:str) -> Image:
    image = Image.open(path)
    return image

sales_data = get_data("db/csv/Superstore Orders.csv")
image = get_image("db/img/supermarket.jpg")

st.sidebar.image(image, use_column_width=True)
st.sidebar.header("Filter Your Data")

try:
    region = st.sidebar.multiselect(
        "Select The Region",
        options=["South", "Central", "East", "West"]
    )

    if region:
        state = st.sidebar.multiselect(
            "Select the State",
            options=sales_data[sales_data["Region"].isin(region)]["State"].unique()
        )
    else:
        state = st.sidebar.multiselect(
            "Select the State",
            options=sales_data["State"].unique()
        )

    if state:
        city = st.sidebar.multiselect(
            "Select the City",
            options=sales_data[sales_data["State"].isin(state)]["City"].unique()
        )
    elif region:
        city = st.sidebar.multiselect(
            "Select the City",
            options=sales_data[sales_data["Region"].isin(region)]["City"].unique()
        )
    else:
        city = st.sidebar.multiselect(
            "Select the City",
            options=sales_data["City"].unique()
        )
    
    category = st.sidebar.multiselect(
        "Select the Category",
        options=sales_data["Category"].unique()
    )

    if category:
        sub_category = st.sidebar.multiselect(
            "Select the Sub-Category",
            options=sales_data[sales_data["Category"].isin(category)]["SubCategory"].unique()
        )
    else:
        sub_category = st.sidebar.multiselect(
            "Select the Sub-Category",
            options=sales_data["SubCategory"].unique()
        )

    if sub_category:
        product_name = st.sidebar.multiselect(
            "Select the Product Name",
            options=sales_data[sales_data["SubCategory"].isin(sub_category)]["ProductName"].unique()
        )
    elif category:
        product_name = st.sidebar.multiselect(
            "Select the Product Name",
            options=sales_data[sales_data["Category"].isin(category)]["ProductName"].unique()
        )
    else:
        product_name = st.sidebar.multiselect(
            "Select the Product Name",
            options=sales_data["ProductName"].unique()
        )

except Exception as e:
    pass

finally:

    if region:
        sales_data = sales_data.query("Region in @region")    
    
    if category:
        sales_data = sales_data.query("Category in @category")
       
    if city:
        sales_data = sales_data.query("City in @city")

    if state:
        sales_data = sales_data.query("State in @state")

    if sub_category:
        sales_data = sales_data.query("SubCategory in @sub_category")
    
    if product_name:
        sales_data = sales_data.query("ProductName in @product_name")


# # ---- MAINPAGE ----
st.title(":bar_chart: Sales Dashboard")
st.markdown("##")

# TOP KPI
total_sales    = int(sales_data["Sales"].sum())
profit_earned  = int(sales_data["Profit"].sum())
sales_forecast = int(sales_data["Sales Forecast"].sum())

left_column, middle_column, right_column = st.columns(3)

left_column.metric(label="Sales Forecast",
                    value=f"${sales_forecast:,}")

middle_column.metric(label="Total Sales",
                    value=f"${total_sales:,}",
                    delta= (total_sales - sales_forecast))

right_column.metric(label="Total Profit",
                    value=f"${profit_earned:,}")

st.markdown("""---""")

# BAR CHART
_, middle_column, _ = st.columns([1, 2, 1])

with middle_column:
    fig = go.Figure(go.Bar(
                x=[total_sales, profit_earned, sales_forecast],
                y=['Total Sales', 'Profit', 'Sales Forecast'],
                marker=dict(
                color='rgba(246, 78, 139, 0.6)',
                line=dict(color='rgba(246, 78, 139, 1.0)', width=3)
        ),
                orientation='h'))
    fig.update_layout(title_text='Profit and Sales Distribution')
    st.plotly_chart(fig)

sales_segment_profit = sales_data.groupby('Segment')['Profit'].sum().reset_index().sort_values(['Profit'], 
                                                                                  ascending=False)
# PIE CHARTS
labels = sales_segment_profit['Segment']
value  = sales_segment_profit['Profit']
profit_pie = go.Figure(data=[go.Pie(labels=labels, values=value, 
                        texttemplate=([f"${v}" for v in value]))])
profit_pie.update_layout(
    title_text="Profit By Customer Segmentation",
    annotations=[dict(text='Profit Segmentation', x=0.5, y=0.5, font_size=10, showarrow=False)])                        

profit_pie.update_traces(hole=.5, hoverinfo="label")

sales_segment_sales = sales_data.groupby('Segment')['Sales'].sum().reset_index().sort_values(['Sales'],
                                                                                    ascending=False)

labels = sales_segment_sales['Segment']
value  = sales_segment_sales['Sales']
sales_pie = go.Figure(data=[go.Pie(labels=labels, values=value,
                        texttemplate=([f"${v}" for v in value]))])
sales_pie.update_layout(
    title_text="Sales By Customer Segmentation",
    annotations=[dict(text='Sales Segmentation', x=0.5, y=0.5, font_size=10, showarrow=False)])
sales_pie.update_traces(hole=.5, hoverinfo="label")


first_chart, second_chart = st.columns(2)
first_chart.plotly_chart(profit_pie, use_container_width=True)
second_chart.plotly_chart(sales_pie, use_container_width=True)

# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
