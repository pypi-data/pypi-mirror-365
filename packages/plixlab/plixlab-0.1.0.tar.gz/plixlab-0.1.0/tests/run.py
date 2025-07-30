import msgpack
import numpy as np
import matplotlib.pyplot as plt
import os
from plixlab import Slide,Presentation
from plixlab.utils import normalize_dict
import plotly.express as px
from bokeh.plotting import figure, show
import dash_bio as dashbio
import pandas as pd


# Prefix for paths
#prefix = 'tests'
prefix = 'reference'
assets_prefix = 'assets'
#prefix = '../docs/source/_static'

def load_data(filename):
    """
    Load reference data from a file.
    """
    with open(f'{prefix}/{filename}.plx', 'rb') as f:
        return normalize_dict(msgpack.unpackb(f.read()))

def generate_or_validate(slide,pytestconfig):
    """
    Handle generating or validating reference data for a given slide.
    """
    filename = slide.title
    generate_references = pytestconfig.getoption("--generate-references")
  
    if generate_references:
      
        # Generate and save reference data
        path = f'{prefix}/{filename}'
        slide.save(path)
        print(f"Reference data for {path} generated.")
    else:
        # Validate against reference data
        data = normalize_dict(slide.get_data())
        reference = load_data(filename)

        assert data == reference, f"Data does not match the reference for {filename}!"


def test_citation(pytestconfig):
    """
    Test citation functionality.
    """
   
    slide = Slide('citation').cite(key='einstein1935',bibfile = f'{assets_prefix}/biblio.bib')

    generate_or_validate(slide, pytestconfig)


def test_welcome(pytestconfig):
   """
   Test welcome functionality.
   """

   slide = Slide('welcome').text('Welcome to Plix!')

   generate_or_validate(slide,pytestconfig)

def test_logo(pytestconfig):
   """
   Test logo functionality.
   """

   slide = Slide('logo').text('Welcome to Plix!').img(f'{assets_prefix}/logo.png',y=0.1,w=0.2)

   generate_or_validate(slide,pytestconfig)

def test_markdown(pytestconfig):
    """
    Test markdown functionality.
    """
    
    slide = Slide('markdown').text(
        '<u> This </u> **text** is *really important*.', 
        x=0.2, y=0.6, fontsize=0.1, color='orange'
    )
    generate_or_validate(slide,pytestconfig)

def test_equation(pytestconfig):
    """
    Test equation.
    """
    
    slide = Slide('equation').text(
        r'''$-C\frac{\partial T}{\partial t} - \nabla \cdot \left(\kappa \nabla T\\right) = Q$''')

    generate_or_validate(slide,pytestconfig)



def test_image(pytestconfig):
    """
    Test image functionality.
    """
    
    slide = Slide('image').img(f'{assets_prefix}/image.png',x=0.2,y=0.3,w=0.65)
    
    generate_or_validate(slide,pytestconfig)


def test_matpltlib(pytestconfig):
    """
    Test matplotlib functionality.
    """
    
    style_file = f'{prefix}/assets/mpl_style_light'
    
    if os.path.exists(style_file):
     plt.style.use(style_file)
    else:
     print(f"Style file not found: {style_file}")
  
    # Create data points
    x = np.linspace(0, 2 * np.pi, 100)
    y = np.sin(x)
  
    # Plot the sine wave
    fig = plt.figure(figsize=(8, 4.5))
    plt.plot(x, y, label='Sine Wave')
    plt.title('Simple Sine Wave')
    plt.xlabel('x values')
    plt.ylabel('y values')

    slide = Slide('matplotlib').matplotlib(fig)
    
    
    generate_or_validate(slide,pytestconfig)   

def test_shape(pytestconfig):
   """
   Test shape functionality.
   """


   slide = Slide('shape').shape('arrow',x=0.2,y=0.45,w=0.2,orientation=45,color=[1,0.015,0]).\
              shape('square',x=0.6,y=0.5,w=0.2,aspect_ratio=0.25)
   generate_or_validate(slide,pytestconfig)   


def test_embed(pytestconfig):
   """
   Test embed functionality.
   """
   url = 'https://examples.pyscriptapps.com/antigravity/latest/'
   slide = Slide('embed').embed(url)

   generate_or_validate(slide,pytestconfig)   



def test_youtube(pytestconfig):
   """
   Test youtube functionality.
   """

   slide = Slide('youtube').youtube('zDtx6Z9g4xA')

   generate_or_validate(slide,pytestconfig)       



def test_plotly(pytestconfig):
   """
   Test plotly functionality.
   """

   df = px.data.iris()

   fig = px.scatter(df, x="sepal_width", \
                   y="sepal_length", \
                   color="species")

   slide = Slide('plotly').plotly(fig)
   

   generate_or_validate(slide,pytestconfig)   

def test_bokeh(pytestconfig):
   """
   Test bokeh functionality.
   """

   x = [1, 2, 3, 4, 5]
   y = [6, 7, 2, 4, 5]

   p = figure(
   x_axis_label='x',
   y_axis_label='y'
   )

   p.line(x, y, legend_label="Temp.", line_width=2)
 
   slide = Slide('bokeh').bokeh(p)

   generate_or_validate(slide,pytestconfig)           

def test_protein(pytestconfig):
   """
   Test protein functionality.
   """

   slide = Slide('protein').molecule('9B31')

   generate_or_validate(slide,pytestconfig) 

def test_python(pytestconfig):
   """
   Test python functionality.
   """

   slide = Slide('python')

   generate_or_validate(slide,pytestconfig)

def test_model(pytestconfig):
   """
   Test model functionality.
   """

   credits  = 'Blue Flower Animated" (https://skfb.ly/oDIqT) by morphy.vision is licensed under Creative Commons Attribution (http://creativecommons.org/licenses/by/4.0/).'

   slide = Slide('model').model3D(f'{assets_prefix}/model.glb').text(credits,y=0.1,fontsize=0.03)

   generate_or_validate(slide,pytestconfig)                 


def test_presentation(pytestconfig):
   """
   Test presentation functionality.
   """

   s1 = Slide().text('Welcome to Plix!')

   df = px.data.iris()

   fig = px.scatter(df, x="sepal_width", \
                   y="sepal_length", \
                   color="species")

   s2 = Slide().plotly(fig)

   presentation = Presentation([s1,s2],title='presentation')

   generate_or_validate(presentation,pytestconfig)   


def test_volcano(pytestconfig):
   """
   Test volcano functionality.
   """


   df = pd.read_csv('https://git.io/volcano_data1.csv')

   fig=dashbio.VolcanoPlot(dataframe=df)

   slide = Slide('volcano').plotly(fig)

   generate_or_validate(slide,pytestconfig)



def test_animation(pytestconfig):
   """
   Test animation functionality.
   """

   slide = Slide('animation').text('Text #1',y=0.7).\
           text('Text #2',y=0.5,animation= 1).\
           text('Text #3',y=0.3,animation= 2)

   generate_or_validate(slide,pytestconfig)


if __name__ == '__main__':

    # Simulate pytestconfig for testing manually
    class MockPytestConfig:
        def getoption(self, option):
            if option == "--generate-references":
                return True  # Change to True to generate references

    # Create a mock pytestconfig instance
    pytestconfig = MockPytestConfig()

    # Run the test function
    test_citation(pytestconfig)
    test_markdown(pytestconfig)
    test_equation(pytestconfig)
    test_image(pytestconfig)
    test_matplotlib(pytestconfig)
    test_shape(pytestconfig)
    test_embed(pytestconfig)
    test_youtube(pytestconfig)
    test_plotly(pytestconfig)
    test_bokeh(pytestconfig)
    test_protein(pytestconfig)
    test_presentation(pytestconfig)
    test_volcano(pytestconfig)
    test_animation(pytestconfig)



