import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt 
import seaborn as sns
sns.axes_style()
custom = {"axes.edgecolor": "grey", "grid.linestyle": "dashed"}
sns.set_style("white", rc = custom)
card_style1 = """padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); background-color: #f7f7f7;"""


from amazon_pipeline import search
# Page setting
st.set_page_config(layout="wide")

def plot_best_seller_rating(column):
    column.markdown(f'''<div style= "background-color: #f7f7f7; padding-left: 20px; padding-top: 10px; margin-bottom : -50px"> 
                    <h4 style= "color: #FF9900;"> Bestseller ratings </h4> </div>''', unsafe_allow_html=True)

    # Create sample data
    labels = ['5', '4', '3', '2', '1']
    sizes = [best_sellers["5_star_percent"][0], best_sellers["4_star_percent"][0], best_sellers["3_star_percent"][0],
             best_sellers["2_star_percent"][0], best_sellers["1_star_percent"][0]]

    # Find the index of the largest segment
    largest_index = sizes.index(max(sizes))

    # Create a pie chart for the outer ring
    fig, ax = plt.subplots()
    fig.set_facecolor('#f7f7f7')  # Set figure background color to black
    ax.set_facecolor('#f7f7f7') 
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='', startangle=90,
                                      colors=['#FF9900', '#5A5A5A', 'grey' , "#c0c0c0",'lightgrey' ], wedgeprops=dict(width=0.3, edgecolor='w'))

    # Add percentage label on top of the largest segment
    autotexts[largest_index].set_text(f'{sizes[largest_index]:.0f}%')

    # Draw a white circle in the center to create the inner hole
    centre_circle = plt.Circle((0, 0), 0.70, fc='#f7f7f7')
    fig.gca().add_artist(centre_circle)

    # Equal aspect ratio ensures the pie chart is circular
    ax.axis('equal')
    ax.set_xlabel("Percentage of star rating", fontsize= 12)

    # Remove default legend to prevent duplicate labels
    ax.legend().set_visible(False)

    column.pyplot(fig)


with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


################################## Title layout ##########################################
# Create a single column layout
column = st.columns([1, 3])
# Display a title image
title_image = "amazon.png"  # Replace with the path to your image file
column[0].image(title_image, width=230)
# Display the title in a larger column
# column[1].title("Amazon Product Reviews Dashboard")
column[1].write("<div style='margin-top: 50px;'><h1 style='color: #5A5A5A;'>Amazon Product Reviews Dashboard</h1></div>", unsafe_allow_html=True)


#################################### Search layout ########################################
# Add css to make text bigger
tabs_font_css = """ <style> div[class*="stTextInput"] label p { font-size: 26px; } </style> """
st.write(tabs_font_css, unsafe_allow_html=True)
input_value = st.text_input( "Search any product!", "")

# Call the function and display the result
if st.button("Search") and input_value != "":
    placeholder = st.empty()
    placeholder.write("Thanks for your input. Scraping data... Generating report.. this might take a few minutes...")
    result = search(input_value)
    # amazon_data, top_products = search(input_value)
    
    # st.write("Result:", result)
    placeholder.empty()

    top_products= pd.read_csv("data/top_products_by_ratings.csv")
    amazon_data= pd.read_csv("data/amazon_data.csv")
    best_sellers= amazon_data[amazon_data["is_best_seller"] == True].reset_index(drop=True)

    column = st.columns([1, 1, 1])
    if len(best_sellers) > 0:
        ###################################### Best Seller layout ###############################################
        image_link= best_sellers["img_link"][0]
        title= best_sellers["title"][0].split(",")[0].split("|")[0] 
        # column[0].markdown(f'''<div style= "background-color: #f7f7f7; padding-left: 20px;"> </div>''', unsafe_allow_html=True)
        column[0].markdown(f'''<div style="{card_style1}">
                            <h4 style= "color: #FF9900; "> Bestseller </h4>
                           <a style= "color: grey;" href= "{best_sellers["product_link"][0]}"/> <p style= "font-size: 18px;"> {title}  </p>
                           <img src="{image_link}" alt="Amazon Product Image" style="height: 170px"> </div>''',unsafe_allow_html=True)

        plot_best_seller_rating(column[1])

        header_css= " margin-bottom: -20px; text-align: center; color: grey;"

        column[2].markdown(f'''<div style="{card_style1}">
                            <h4 style= "color: #FF9900; padding-left: 20px;"> Best seller ratings and reviews </h4>
                            <h4 style= "{header_css}"> Total ratings </h4>
                            <h1 style= "color: grey; text-align: center; margin-bottom: -10px;">  {int(best_sellers["total_ratings"][0])}  </h2>
                            <h4 style= "{header_css}"> Total reviews </h4> 
                            <h1 style= "color: grey; text-align: center; margin-bottom: -10px;"> {int(best_sellers["total_reviews"][0])}  </h2>
                             </div>''',unsafe_allow_html=True)

    else:
        st.markdown(f'''<div style="{card_style1}">Oops looks like there was no Best seller in results </div>''',unsafe_allow_html=True)



    column = st.columns([3, 1])
    ###################### Top products by rating #########################################
    card_style = """padding: 15px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); background-color: #f7f7f7;"""
    column[0].markdown(f'''<div> <h4 style= "color: #FF9900; {card_style}"> Top products by rating </h4> </div>''', unsafe_allow_html=True)    

    html_table = f"""
    <table style="background-color: #f7f7f7; width:100%">
      <tr><td> <a style= "color: grey;" href= "{top_products["product_link"][0]}"/> {top_products["title"][0]}</td><td>{top_products['rating'][0]}</td></tr>
      <tr><td> <a style= "color: grey;" href= "{top_products["product_link"][1]}"/> {top_products["title"][1]}</td><td>{top_products['rating'][1]}</td></tr>
      <tr><td> <a style= "color: grey;" href= "{top_products["product_link"][2]}"/> {top_products["title"][2]}</td><td>{top_products['rating'][2]}</td></tr>
      <tr><td> <a style= "color: grey;" href= "{top_products["product_link"][3]}"/> {top_products["title"][3]}</td><td>{top_products['rating'][3]}</td></tr>
      <tr><td> <a style= "color: grey;" href= "{top_products["product_link"][4]}"/> {top_products["title"][4]}</td><td>{top_products['rating'][4]}</td></tr>
    </table>
    """

    # Render the HTML table using Markdown
    column[0].markdown(html_table, unsafe_allow_html=True)

    ########################### Top products average price ############################
    column[1].markdown(f'''<div style="{card_style1}"> 
                       <h4 style= "color: #FF9900; margin-top: -10px; text-align: center;"> Average price </h4>
                       <p style= "margin: -20px 0px -10px 0px; text-align: center; "> ( Top products by rating ) </p>
                       <h1 style= "color: grey; text-align: center; font-size: 50px"> {round(top_products["price"].mean())}</h1>
                       <h6 style= "text-align: center; margin-top: -20px; margin-bottom: -30px "> INR </h6>
                       </div>''',unsafe_allow_html=True)

    column[1].markdown(f'''<div style="margin-top : 10px; {card_style1}"> 
                       <h4 style= "color: #FF9900; margin-top: -10px; text-align: center;"> Average Rating </h4>
                       <p style= "margin: -20px 0px -30px 0px; text-align: center; "> ( Top products by rating ) </p>
                       <h1 style= "color: grey; text-align: center; font-size: 50px"> {round(top_products["rating"].mean())}</h1>
                       </div>''',unsafe_allow_html=True)




    column = st.columns([1,2,1])
    ###################### Distribution plot for price ########################################
    column[1].markdown(f'''<div style= "margin : 10px 0 -50px 0; {card_style}"> 
                       <h4 style= "color: #FF9900; margin-top: -20px;">Product distribution by price</h4></div>''', unsafe_allow_html=True)
    fig,ax = plt.subplots()
    fig.set_size_inches(6, 2)
    plt.tick_params(left=False, right=False, labelleft=False, labelbottom=True)
    # ax.set_facecolor('none')
    for spine in ax.spines.values():
        spine.set_visible(False)

    counts, edges, bars = ax.hist(amazon_data["price"], bins= 15 ,color="#FF9900")

    ax.set_ylabel("Number of products", fontsize = 10, fontweight ='bold')
    ax.set_xlabel("Price")
    plt.box(False)
    def format_func(value, tick_number):
        if value > 1000:
            K_value = float(value / 1000)
            return f"{K_value}K"
        return round(value)

    ax.xaxis.set_major_formatter(plt.FuncFormatter(format_func))
    fig.set_facecolor('#f7f7f7')  # Set figure background color to black
    ax.set_facecolor('#f7f7f7') 

    column[1].pyplot(fig)


    ###################### Positive vs Negative plot ########################################
    column[0].markdown(f'''<div style= "margin : 10px 0 -40px 0; {card_style} padding-top: -20px;"> 
                       <h5 style= "color: #FF9900;"> Positive vs Critical reviews  </h5></div>''', unsafe_allow_html=True)
    fig,ax = plt.subplots()
    plt.tick_params(left=False, right=False, labelleft=False, labelbottom=True)

    x= ["positive", "critical"]
    y= [round(amazon_data["total_positive_reviews"].mean()), 
        round(amazon_data["total_critical_reviews"].mean())]
    plt.bar(x, y,color=["#FF9900", "lightgrey"] ) 
    plt.ylabel("Number of reviews", fontsize = 20 )
    plt.xticks(fontsize=20)
    fig.set_facecolor('#f7f7f7')  # Set figure background color to black
    ax.set_facecolor('#f7f7f7') 
    plt.box(False)
    for i in range(len(x)):
        plt.text(i,y[i],y[i], ha= "center", fontsize= 20)


    column[0].pyplot(fig)

    #################################### Average cards ############################################
    column[2].markdown(f'''<div style="margin-top: 10px; {card_style1} "> 
                       <h4 style= "color: #FF9900; margin-top: -10px; text-align: center;"> Average Positive Reviews </h4>
                       <h1 style= "margin: -40px 0 -20px; color: grey; text-align: center; font-size: 50px"> {round(top_products["total_positive_reviews"].mean())}</h1>
                       </div>''',unsafe_allow_html=True)

    column[2].markdown(f'''<div style="margin-top: 7px; {card_style1}"> 
                       <h4 style= "color: #FF9900; margin-top: -10px; text-align: center;"> Average Critical Reviews </h4>
                       <h1 style= "margin: -40px 0 -20px; color: grey; text-align: center; font-size: 50px"> {round(top_products["total_critical_reviews"].mean())}</h1>
                       </div>''',unsafe_allow_html=True)
else:
    pass