import cairo
import base64
from io import BytesIO
import numpy as np
 
 
def hex_to_rgb(hex_color):
    """
    Convert a hexadecimal color string to an RGB tuple.

    :param hex_color: Hexadecimal color string (e.g., "#FFFFFF")
    :return: RGB tuple
    """
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def arrow(context, s, a, b, c, d):

    a *= s
    b *= s
    c *= s
    d *= s

    context.move_to( 0,   c/2    )
    context.line_to( 0,   c/2 + b)
    context.line_to( d,   0      )
    context.line_to( 0,  -c/2 - b)
    context.line_to( 0,  -c/2    )
    context.line_to(-a,  -c/2    )
    context.line_to(-a,   c/2    )
    context.line_to( 0,   c/2    )   
    context.close_path()
    context.stroke()


def square(context,s,a,b):

    a *= s
    b *= s

    context.move_to( -a/2,    a/2 - b    )
    context.line_to(  a/2,    a/2 - b   )
    context.line_to(  a/2,   a/2    )
    context.line_to( -a/2,   a/2    )
    context.line_to( -a/2,    a/2 - b    )
    context.close_path()
    context.stroke()



def run(shapeID,**argv) :
 
    scale = 300
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, scale, scale)     

    context = cairo.Context(surface)

    context.translate(scale/2, scale/2)

    context.set_line_width(0.01*scale)

    color = argv.setdefault('color',(1,1,1))
    if color[0] == '#':
        """Convert to RGB"""
        color = np.array(hex_to_rgb(color))/255

    context.set_source_rgb(*color)

    # Save the current context state
    context.save()

    # Rotate the context by the given orientation
    orientation = argv.setdefault('orientation',0)
    orientation *=np.pi/180
    context.rotate(-orientation)


    # Call the function
    if shapeID == 'arrow':

     arrow(context,scale,0.5,0.15,0.25,0.2)


    elif shapeID == 'square': 
     aspect_ratio = argv.setdefault('aspect_ratio',0.5)
     
     square(context,scale,1,aspect_ratio)

    else: 
       raise f'No shape recognized {shapeID}' 
    
    

    buf = BytesIO()
    surface.write_to_png(buf)
    buf.seek(0)
    url = buf.getvalue()
    buf.close()

    return url



 
