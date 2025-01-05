import streamlit as st
#from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """
    Choose the fruits you want in your custom smoothie!
    """
)

# Input for the name on the smoothie
name_on_order = st.text_input("Name On The Smoothie")
st.write("The Name On Your Smoothie will be:", name_on_order)

# Get the active Snowflake session
#session = get_active_session()
cnx = st.connection("snowflake") 
session = cnx.session()
# Select the FRUIT_NAME column from the specified table
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Display the dataframe in the Streamlit app
st.dataframe(data=my_dataframe, use_container_width=True)

# Multi-select for ingredients
ingredients_list = st.multiselect("Choose up to 5 ingredients:", my_dataframe.collect(),max_selections =5)

# Display and process selected ingredients if any are chosen
if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)
    st.write(ingredients_string)
    
    # SQL insert statement
    my_insert_stmt = f"""INSERT INTO smoothies.public.orders(ingredients, name_on_order)
                         VALUES ('{ingredients_string}', '{name_on_order}')"""

    # Button to submit the order
    time_to_liner = st.button("Submit Order")
    if time_to_liner:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")

import requests
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
st.text(smoothiefroot_response)
