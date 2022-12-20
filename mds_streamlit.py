#!/usr/bin/env python
# coding: utf-8

# In[ ]:



####################################### Import Libraries #######################################
import streamlit as st
import pandas as pd
import numpy as np
import streamlit.components.v1 as components
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.colors as clr
import plotly.figure_factory as ff
from PIL import Image
from streamlit_elements import dashboard
from contextlib import contextmanager
from abc import ABC, abstractmethod
from types import SimpleNamespace
from uuid import uuid4
import json
from streamlit_elements import mui, editor, sync, lazy
from streamlit_elements import nivo
from streamlit_elements import elements, mui, html
from streamlit import session_state as state
from sklearn.manifold import TSNE
import plotly.graph_objects as go
import seaborn as sns
import hydralit as hy
import hydralit_components as hc
from hydralit import HydraHeadApp
from hydralit_components import HyLoader, Loaders

class Dashboard:

    DRAGGABLE_CLASS = "draggable"

    def __init__(self):
        self._layout = []

    def _register(self, item):
        self._layout.append(item)

    @contextmanager
    def __call__(self, **props):
        # Draggable classname query selector.
        props["draggableHandle"] = f".{Dashboard.DRAGGABLE_CLASS}"

        with dashboard.Grid(self._layout, **props):
            yield

    class Item(ABC):

        def __init__(self, board, x, y, w, h, **item_props):
            self._key = str(uuid4())
            self._draggable_class = Dashboard.DRAGGABLE_CLASS
            self._dark_mode = False
            board._register(dashboard.Item(self._key, x, y, w, h, **item_props))

        def _switch_theme(self):
            self._dark_mode = not self._dark_mode

        @contextmanager
        def title_bar(self, padding="5px 15px 5px 15px", dark_switcher=True):
            with mui.Stack(
                className=self._draggable_class,
                alignItems="center",
                direction="row",
                spacing=1,
                sx={
                    "padding": padding,
                    "borderBottom": 1,
                    "borderColor": "divider",
                },
            ):
                yield

                if dark_switcher:
                    if self._dark_mode:
                        mui.IconButton(mui.icon.DarkMode, onClick=self._switch_theme)
                    else:
                        mui.IconButton(mui.icon.LightMode, sx={"color": "#ffc107"}, onClick=self._switch_theme)

        @abstractmethod
        def __call__(self):
            """Show elements."""
            raise NotImplementedError
            
class Editor(Dashboard.Item):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._dark_theme = True
        self._index = 0
        self._tabs = {}
        self._editor_box_style = {
            "flex": 1,
            "minHeight": 0,
            "borderBottom": 1,
            "borderTop": 1,
            "borderColor": "divider"
        }

    def _change_tab(self, _, index):
        self._index = index

    def update_content(self, label, content):
        self._tabs[label]["content"] = content

    def add_tab(self, label, default_content, language):
        self._tabs[label] = {
            "content": default_content,
            "language": language
        }

    def get_content(self, label):
        return self._tabs[label]["content"]

    def __call__(self):
        with mui.Paper(key=self._key, sx={"display": "flex", "flexDirection": "column", "borderRadius": 3, "overflow": "hidden"}, elevation=1):

            with self.title_bar("0px 15px 0px 15px"):
                mui.icon.Terminal()
                mui.Typography("Editor")

                with mui.Tabs(value=self._index, onChange=self._change_tab, scrollButtons=True, variant="scrollable", sx={"flex": 1}):
                    for label in self._tabs.keys():
                        mui.Tab(label=label)

            for index, (label, tab) in enumerate(self._tabs.items()):
                with mui.Box(sx=self._editor_box_style, hidden=(index != self._index)):
                    editor.Monaco(
                        css={"padding": "0 2px 0 2px"},
                        defaultValue=tab["content"],
                        language=tab["language"],
                        onChange=lazy(partial(self.update_content, label)),
                        theme="vs-dark" if self._dark_mode else "light",
                        path=label,
                        options={
                            "wordWrap": True
                        }
                    )

            with mui.Stack(direction="row", spacing=2, alignItems="center", sx={"padding": "10px"}):
                mui.Button("Apply", variant="contained", onClick=sync())
                mui.Typography("Or press ctrl+s", sx={"flex": 1}) 
                             
                    
####################################### Read Relevant Data #######################################
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
cmap_cf = clr.LinearSegmentedColormap.from_list('custom cf', ['#5FBF6D','#34503A'], N=256) ## conditional formatting colormap

# path = '/home/ec2-user/mds_data/streamlit/data/'

static_data1 = pd.read_csv('static_data1.csv') #
demo_data = pd.read_csv('demographics_data1.csv') #
tsne_data = 'tsne_plot.png'

#------------------------------------------adding top menu-----------------------------------------------------------------------
over_theme = {'txc_inactive': 'White','menu_background':'gray','txc_active':'black'}
app = hy.HydraApp(title='MG App',
#                   use_navbar=True,
#                   navbar_sticky=False,
                  navbar_theme=over_theme)  

####################################### Title #######################################
one = True
two=False
three=False
col1,col2,col3 = st.columns([4,1,1])
m = st.markdown("""
<style>
div.stButton > button:first-child {
    height: 3em;
width: 12em; 
font-size:24px !important;
border-radius: 20%;
}
</style>""", unsafe_allow_html=True)

with col1:
    st.markdown("<h1 style='text-align: left; margin-top: -50px;'>Wayfinder - Myelodysplastic syndrome</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: left; margin-top: -30px;'><i>Very High/High/Intermediate Risk Patients - 1st MDS Diagnosis to 2 Years</i></h3>", unsafe_allow_html=True)

# with col2:
#     one = st.button("Cluster Profiles")
# with col3:
#     two = st.button("Cluster Deep-Dive")
    
def set_current_page(page,page_name):
    one = False
    two = False
    three = False
    page = True   
    current_page = page_name
    
if one == True:
    set_current_page(one,"one")
elif two == True:
    set_current_page(two,"two")
elif three == True:
    set_current_page(three,"three")
else:
    one = True
components.html("<div style = 'background-color:#333; height:50px; border-radius:5px; margin:0; padding:0'></div>",height=10)

####################################### adding sidebar #######################################

options = st.sidebar
with options:
    st.header("WayFinder Filters")
#     time_period = st.slider("TIME FRAME",2014,2022)
    
#     insight = st.selectbox("INSIGHT",["Business Rules","Business Rules + ML"])
#     st.write(insight)
    
#     if current_page == "one":
    filter_data = pd.DataFrame([
    #         ["Data Source","Cohort","Total Patients","Known Patients","Criteria"],
            ["SHS Claims","Myasthenia Gravis","29000","16000","Patients who have no history of lung or respiratory problems"],
            ["","Breast Cancer","30000","19000","Patients who have no history of cancer in family"],
            ["","NSCLC","39000","15000","Patients who have no history of lung or respiratory problems"]
        ])

    data_source = st.selectbox("DATA SOURCE",pd.unique(filter_data[0]))
    filter_data = (filter_data[filter_data[0]==data_source]).reset_index()
    patient_cohort = st.selectbox("PATIENT COHORT",pd.unique(filter_data[1]))

####################################### Section1: Cluster Profiles #######################################
 
        
########################################### draggable class #######################################
#if one == True:
@app.addapp()
def Executive_Summary():
    
    st.subheader("What are the key Patient Segments and corresponding distribution?")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        txt = st.text_area('', '''ARCHETYPE P1

         - Very High treatment rate and visits to Oncologists
         - Severe patients with high adverse event prevalence such as thrombocytopenia, white blood cell disorders etc.
         - High frequency of monitoring activity and lab tests

    ''', height=200)
        components.html(
        """
        <div class="card" style="width: 27rem; height: 15rem; background-color: #92D0AA; border-radius: 20px; border-style: solid; border-color: #195A32">
          <div class="card-body">
            <h3 class="card-title" style="color: white; font-family: Arial, Helvetica, sans-serif; text-align:center; font-size:22px"><i>Archetype P1</i></h3>
            <p class="card-text" style="font-size:20px; font-family: Arial">&nbsp;&nbsp;Number of Patients: <b>"""+static_data1['Cluster 1'][0]+"""</b></p>

            <p class="card-text" style="font-size:20px; font-family: Arial">&nbsp;&nbsp;%Male: <b>"""+static_data1['Cluster 1'][1]+"""</b></p>
            <p class="card-text" style="font-size:20px; font-family: Arial">&nbsp;&nbsp;Average age at 1st MDS Dx: <b>"""+static_data1['Cluster 1'][2]+"""</b></p>
          </div>
        </div>
        """, height=270, width=450)
    #  "{:,}".format(analytical_data[analytical_data['cluster']==c]['provid_fin'].nunique())  
    with col2:
        txt = st.text_area('', '''ARCHETYPE P2

         - Moderate treatment rate 
         - High adverse event prevalence
         - Moderate frequency of monitoring and lab test activity

    ''', height=200)
        components.html(
        """
        <div class="card" style="width: 27rem; height: 15rem; background-color: #4B9ABB; border-radius: 20px; border-style: solid; border-color: #3B4068">
          <div class="card-body">
            <h3 class="card-title" style="color: white; font-family: Arial, Helvetica, sans-serif; text-align:center; font-size:22px"><i>Archetype P2</i></h3>
            <p class="card-text" style="font-size:20px; font-family: Arial">&nbsp;&nbsp;Number of Patients: <b>"""+static_data1['Cluster 2'][0]+"""</b></p>

            <p class="card-text" style="font-size:20px; font-family: Arial">&nbsp;&nbsp;%Male: <b>"""+static_data1['Cluster 2'][1]+"""</b></p>
            <p class="card-text" style="font-size:20px; font-family: Arial">&nbsp;&nbsp;Average age at 1st MDS Dx: <b>"""+static_data1['Cluster 2'][2]+"""</b></p>
          </div>
        </div>
        """, height=270, width=450)

    with col3:
        txt = st.text_area('', '''ARCHETYPE P3

         - Low treatment rate
         - Lower adverse events and comorbidities as compared to other high-risk patients
         - Fast progression to AML
         - Low monitoring activity and lab tests 

    ''', height=200)
        components.html(
        """
        <div class="card" style="width: 27rem; height: 15rem; background-color: #F2E394; border-radius: 20px; border-style: solid; border-color: #F7C505">
          <div class="card-body">
            <h3 class="card-title" style="color: white; font-family: Arial, Helvetica, sans-serif; text-align:center; font-size:22px"><i>Archetype P3</i></h3>
            <p class="card-text" style="font-size:20px; font-family: Arial">&nbsp;&nbsp;Number of Patients: <b>"""+static_data1['Cluster 3'][0]+"""</b></p>

            <p class="card-text" style="font-size:20px; font-family: Arial">&nbsp;&nbsp;%Male: <b>"""+static_data1['Cluster 3'][1]+"""</b></p>
            <p class="card-text" style="font-size:20px; font-family: Arial">&nbsp;&nbsp;Average age at 1st MDS Dx: <b>"""+static_data1['Cluster 3'][2]+"""</b></p>
          </div>
        </div>
        """, height=270, width=450)

    with col4:
        txt = st.text_area('', '''ARCHETYPE P4
         
         - Low treatment rate and progression to AML
         - Lower adverse events such as thrombocytopenia but higher comorbidities such as connective tissue disorders, osteoarthritis

    ''', height=200)
        components.html(
        """
        <div class="card" style="width: 27rem; height: 15rem; background-color: #EC5923; border-radius: 20px; border-style: solid; border-color: #8E2E07">
          <div class="card-body">
            <h3 class="card-title" style="color: white; font-family: Arial; text-align:center; font-size:22px"><i>Archetype P4</i></h3>
            <p class="card-text" style="font-size:20px; font-family: Arial">&nbsp;&nbsp;Number of Patients: <b>"""+static_data1['Cluster 4'][0]+"""</b></p>

            <p class="card-text" style="font-size:20px; font-family: Arial">&nbsp;&nbsp;%Male: <b>"""+static_data1['Cluster 4'][1]+"""</b></p>
            <p class="card-text" style="font-size:20px; font-family: Arial">&nbsp;&nbsp;Average age at 1st MDS Dx: <b>"""+static_data1['Cluster 4'][2]+"""</b></p>
          </div>
        </div>
        """, height=270, width=450)

    ####################################### Section2: Cluster Distribution #######################################
    col1, col2 = st.columns(2)

    with col1:
        with st.expander("Key Differentiators", expanded=True):
            d = st.selectbox("", tuple(demo_data.columns[1:]))
            fig = px.bar(demo_data, x='Archetype', y=d, color='Archetype', color_discrete_map = {'Archetype P1':'#92D0AA', 'Archetype P2':'#4B9ABB', 'Archetype P3':'#F2E394', 'Archetype P4':'#EC5923'},
                        category_orders={'Archetype':['Archetype P1','Archetype P2','Archetype P3','Archetype P4']}, height=440)
            fig.update_layout(title='% Patients per Cluster')
            fig.update_layout(title_font_size=30)
            fig.update_layout(title_pad_l=270)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        with st.expander("Archetype Visualization", expanded=True):
            st.subheader('Archetype Visualization')
            fig = st.image(Image.open(tsne_data), caption = '')

    st.markdown("""<hr style="height:1px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)


@app.addapp()
def Wayfinder_Archetype_Patient_Journey():
   
    with st.expander("Wayfinder Archetype Journey Comparison", expanded=False):
            fig = st.image(Image.open('overall_wayfinder.PNG'), caption = 'Wayfinder Archetype Visualization')

    st.markdown("""<hr style="height:1px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)

    
    st.subheader("How does Wayfinder Archetype journey's differentiate by Treatment Modality")
    with st.expander("", expanded=True):
        st.write('<style>div.row-widget.stRadio > div{flex-direction:row;justify-content: center;} </style>', unsafe_allow_html=True)
        cluster = st.radio("",('Archetype 1', 'Archetype 2', 'Archetype 3', 'Archetype 4'))
        
        if cluster == 'Archetype 1':
            fig = st.image(Image.open('archetype1.PNG'), caption = 'Wayfinder Archetype1 Visualization')

        elif cluster == 'Archetype 2': 
            fig = st.image(Image.open('archetype2.PNG'), caption = 'Wayfinder Archetype2 Visualization')

        elif cluster == 'Archetype 3': 
            fig = st.image(Image.open('archetype3.PNG'), caption = 'Wayfinder Archetype3 Visualization')

        elif cluster == 'Archetype 4': 
            fig = st.image(Image.open('archetype4.PNG'), caption = 'Wayfinder Archetype4 Visualization')

    st.markdown("""<hr style="height:1px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True) 

    #-----------------------------------------------------------------------------------------------------------------------------    
    st.subheader('How does the events evolve over time across Archetypes ?')

    with st.expander("Event Prevalence per Quarter by Archetype", expanded=False):
        fig = st.image(Image.open('bitplot1.PNG'), caption = '')
        
    #-------------------------------------------- map ---------------------------------------------------------------------------------
    st.markdown("""<hr style="height:1px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)

@app.addapp()
def MDS_Cohort_Patient_Journey():
    
    st.header("How does Risk and Therapy Progression happens in MDS patient ?")
         
    with st.expander("Sankey Plot", expanded=True):
        fig = st.image(Image.open('sankey.PNG'), caption = '')
    
    st.subheader('What are the key events across the patient clusters for Very High Risk Cohort?')
    with st.expander("Event Prevalence per Quarter by Archetype for Very High Risk Cohort", expanded=True):
        fig = st.image(Image.open('very_high.PNG'), caption = '')
    
    st.subheader('What are the key events across the patient clusters for High Risk Cohort?')   
    with st.expander("Event Prevalence per Quarter by Archetype for High Risk Cohort", expanded=True):
        fig = st.image(Image.open('high.PNG'), caption = '')
    
    st.subheader('How does the events evolve over time across Archetypes ?')    
    with st.expander("Event Prevalence per Quarter by Archetype", expanded=True):
        fig = st.image(Image.open('bitplot2.PNG'), caption = '')
    

app.run()