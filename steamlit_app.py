# Import python packages
import streamlit as st 
from snowflake.snowpark.functions import col
import pandas as pd

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!
    """
)

name_on_order = st.text_input("Name on Smoothie:","");


# Get the current credentials
ctx = st.connection("snowflake")
session = ctx.session();
#option = st.selectbox("What is your favorite fruit?",session.table("smoothies.public.fruit_options").columns[1])
#st.write("You have selected: ", option);
 
my_dataframe = session.table("smoothies.public.fruit_options").select((col('FRUIT_NAME'),col('SEARCH_ON')))
pd_df = my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.stop()

ingrediants_list = st.multiselect('Choose up to 5 ingredients',my_dataframe)
import requests
if ingrediants_list:
    st.write(ingrediants_list)
    st.text(ingrediants_list)
    ingredients_string=''

    for item in ingrediants_list:
        ingredients_string += item +' '
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == item,'SEARCH_ON'].iloc[0]
        st.write('The search value for ', item,' is ', search_on, '.')
        url = 'https://fruityvice.com/api/fruit/'+search_on
        st.write(url)
        st.subheader(search_on+' Nutrition Information')
        fruityvice_response = requests.get(url)
        st.write(fruityvice_response.json())        
        fv_df= st.dataframe(data = fruityvice_response.json(),use_container_width=True)

    
    st.write(ingredients_string)


    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,NAME_ON_ORDER )
                values ('""" + ingredients_string + """','"""+name_on_order+"""')"""
    
    st.write(my_insert_stmt)

    time_to_insert  = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
