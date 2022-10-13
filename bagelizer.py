# bagelizer.py

# Bagelizer 9000 - the latest & greatest in bagel software technology.

# IMPORTS
import plotly.express as px
import streamlit as st
import nomad_tools as nomad

# set paths for Streamlit hosted app
logo = '/Users/maxsun/PycharmProjects/trend_data_app/images/P2S LOGO_COLOR.png'

"""
# Bagelizer 9000
the latest & greatest in bagel software technology.

###### Upload a Modifier Sales report from Square.
"""

# st.image('./images/bagel meme.png')
# st.write('more to come soon')

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:

    # import & process modifier sales report - only care about "Bagel Flavor"
    df_mod = nomad.import_modifier_sales(uploaded_file)

    # create & display flavor and category summaries above full dataframe
    flavors, categories = nomad.create_summary(df_mod)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.header("FLAVOR BREAKDOWN")

        # display flavor breakdown and total
        st.dataframe(flavors)
        st.write(flavors['Quantity'].sum())

        # pie chart from flavors
        fig = px.pie(flavors, values='Quantity', names='Flavor', title='Bagel Flavor Breakdown')
        fig.update_traces(textinfo='label+value+percent')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.header("CATEGORY BREAKDOWN")

        # display category breakdown & total
        st.dataframe(categories)
        st.write(categories['Bagels'].sum())

    with col3:
        st.header('MODIFIER SALES DATA')
        st.dataframe(df_mod)


