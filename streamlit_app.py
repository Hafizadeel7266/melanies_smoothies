# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom smoothie!
    """
)

title = st.text_input("Name on Smoothie")
st.write("The name on your smoothie will be:", title)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert Snowpark Dataframe to Pandas Dataframe so we can use the LOC function
pd_df = my_dataframe.to_pandas()

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:
    st.write(ingredients_list)
    ingredients_string = ' '.join(ingredients_list)

    for fruit in ingredients_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit, 'SEARCH_ON'].iloc[0]
        
        if search_on:  # Check if search_on is not None
            st.subheader(fruit + ' Nutrition Information')
            smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
            if smoothiefroot_response.status_code == 200:
                st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
            else:
                st.write(f"Could not retrieve information for {fruit}.")
        else:
            st.write(f"No nutrition information available for {fruit}.")

    my_insert_stmt = f"""INSERT INTO smoothies.public.orders(ingredients, name_on_order)
                         VALUES ('{ingredients_string}', '{title}')"""

    st.write(my_insert_stmt)
    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f"Your smoothie is ordered, {title}!", icon="✅")
