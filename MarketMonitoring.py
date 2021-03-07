from bs4 import BeautifulSoup
import requests
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
from dateutil.relativedelta import *


st.set_page_config(
    page_title="Akcje GPW",
    page_icon="",
    #layout="wide",
    initial_sidebar_state="expanded"
)
st.title('Generator wykresów cen akcji notowanych na GPW')
#st.markdown("""
## Generator wykresu ceny wybranej spółki z Giełdy Papierów Wartościowych w Warszawie
#Dane pochodzą z portalu stooq.pl
#""")

InformationContainer = st.empty()

@st.cache
def PobierzSpolkiGPW():
    
    def getPage(url):
        page = requests.get(url)
        soup = BeautifulSoup(page.text, "html.parser")
        return soup
    
    page_iter = 1       
    Spolki = []
    url = "https://stooq.pl/t/?i=523&v=0&l={}"
    while(1==1):
        page = getPage(url.format(page_iter))
        tabela_z_spolkami = page.find("table", {"id" : "fth1"}).find("tbody")
        if len(tabela_z_spolkami) <= 0 :
            break
        else:
            for wiersz in tabela_z_spolkami:
                Spolki.append([wiersz.find(id = "f13").text, wiersz.find(id = "f10").text])
            page_iter+=1
    return Spolki

    
Spolki = PobierzSpolkiGPW()

@st.cache   
def DownloadPriceData(ChosenCompany):
    download_data_path = 'https://stooq.pl/q/d/l/?s='+ ChosenCompany + '&i=d'
    #st.write(download_data_path)
    Price_Data = requests.get(download_data_path)
    Price_Data = Price_Data.text.split('\r\n')
    Price_Data = [wiersz.split(',') for  wiersz in Price_Data]
    cols = Price_Data[0]
    data = Price_Data[1:]
    df1 = pd.DataFrame(columns = cols, data = data)
    df1 = df1.dropna()
    df1["Zamkniecie"] = pd.to_numeric(df1["Zamkniecie"], downcast="float")
    df1['Data'] = pd.to_datetime(df1['Data'])
    #df1.sort_values(by=['Data'], inplace=True, ascending=False)
    return df1

#add_selectbox = st.sidebar.selectbox(
#    "Jak oceniasz apkę?",
#    ("Dobra", "Średnia", "Zła")
#)

WybranaSpolka_selectbox = st.sidebar.selectbox(
    "Wybierz spółkę",
    ["<wybierz>"]+[item[1] + " ("+item[0]+")" for item in Spolki],
    0 #index of default element
)

@st.cache(allow_output_mutation=True)
def button_states():
    return {"pressed": None}

is_pressed = button_states()  # gets our cached dictionary


if WybranaSpolka_selectbox != "<wybierz>":
    WybranaSpolka_KOD = WybranaSpolka_selectbox[ int(WybranaSpolka_selectbox.find("(")+1) : int(WybranaSpolka_selectbox.find(")")) ] 

    InformationContainer = st.success("Wybrana spółka: " + WybranaSpolka_selectbox)

    #InformationContainer = st.info('Pobieram dane o wybranej spółce...')
    df1 = DownloadPriceData(WybranaSpolka_KOD)
    
    
    ZakresDat_Filter = st.sidebar.slider(
        "Wybierz zakres dat",
        df1["Data"].iloc[-1].date(),
        df1["Data"].iloc[0].date(),
        (df1["Data"].iloc[-1].date(), df1["Data"].iloc[0].date())
        )
    #col1, col2 , col3 , col4, col5, col6, col7= st.sidebar.beta_columns([1,1,1,1,1,1,1])
    #button_2t  = col2.checkbox("2t")
    #if(button_2t):
    #    ZakresDat_Filter = st.sidebar.empty()
    #    ZakresDat_Filter =  st.sidebar.slider(
    #        "Wybierz zakres dat",
    #        df1["Data"].iloc[-1].date(),
    #        df1["Data"].iloc[0].date(),
    #        (df1["Data"].iloc[-1].date() - relativedelta(weeks=2), df1["Data"].iloc[-1].date())
    #    )
    #      
    #
    #     
    #
    #col2.checkbox("1m")
    #col3.button("6m")
    #col4.button("1r")
    #col5.button("2r")
    #col6.button("5r")
    #col7.button("all")
    
    SredniaRuchoma_Filter = st.sidebar.checkbox("Średnia ruchoma")
    #SredniaRuchoma_Filter = col1.checkbox("Srednia Ruchoma")
    SredniaRuchoma_Param1 = st.empty()
    if (SredniaRuchoma_Filter):
        SredniaRuchoma_Param1 = st.sidebar.slider(#col2.slider( #
        
            'Opóźnienie',
            1, 500, 4
        )
    
    if(st.sidebar.button("Generuj Wykres")):
        mask = (df1["Data"] >= ZakresDat_Filter[0]) & (df1["Data"] <= ZakresDat_Filter[1])
        df1 = df1.loc[mask]
        fig, ax = plt.subplots()
        ax.plot(df1['Data'], df1['Zamkniecie'])
        if(SredniaRuchoma_Filter):
            ax.plot(df1['Data'], df1.Zamkniecie.rolling(window = SredniaRuchoma_Param1 ).mean())
               
        ax.grid = True
        fig.autofmt_xdate()
        st.pyplot(fig)
else:
    InformationContainer = st.warning('Wybierz spółkę')


with st.beta_expander("TO DO"):
    st.image("https://www.maccsuso.org.uk/wp-content/uploads/2020/03/things-to-do.png")
    st.write("""
        Filtry na datę. Najlepiej jakieś suwaki fajne z wyłapywaniem błędów typu od > do. 
        Mądre dobieranie dat do wykresu - label i ogólnie nie ma sensu chyba każdej daty prezentować.
        Zaznaczyć dywidendę.
        Dodawanie lini trendu, średniej ruchomej do wyłapywania zmian trendu.
        buttony do zakresu dat sprawić zeby aktualizowaly slider! 
        dodać postawowe wskazniki dla spolki w kontenerze obok
        PORTFEL zrobic z wykorzystaniem klasy. Osobny kontener do tego.
    """
    , )
    

#with st.beta_container():
#    st.write("This is inside the container")
#    
#    # You can call any Streamlit command, including custom components:
#    st.bar_chart(np.random.randn(50, 3))

#st.write(df1['Data'].head(), df1['Zamkniecie'].head())

#p.line(x = df1['Data'], y = df1['Zamkniecie'], legend='Trend', line_width=2)
#fig = plt.plot(df1['Data'], df1['Zamkniecie'])
#options = st.multiselect('What are your favorite colors',['Green', 'Yellow', 'Red', 'Blue'],['Yellow', 'Red'])
#progress_bar = st.progress(0)
#progress_bar.progress(100)
#st.dataframe(df1)