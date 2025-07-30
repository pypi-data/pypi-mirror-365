def normalize_dict(data):
    if isinstance(data, dict):
        return {k: normalize_dict(v) for k, v in data.items()}
    elif isinstance(data, (list, tuple)):
        return [normalize_dict(v) for v in data]
    else:
        return data


def process_bokeh(fig):

     fig.xaxis.major_tick_line_color = "white"
     fig.xaxis.major_label_text_color = "white"
     fig.yaxis.major_tick_line_color = "white"
     fig.yaxis.major_label_text_color = "white"
     fig.xaxis.axis_label_text_color = "white"
     fig.yaxis.axis_label_text_color = "white"
     fig.background_fill_color=None
     fig.border_fill_color=None
     fig.sizing_mode='stretch_both'


def process_plotly(fig):
             

             """Post processing plotly""" 
             fig.update_layout(
             plot_bgcolor='rgba(0,0,0,0)',
             paper_bgcolor='rgba(0,0,0,0)',
             autosize=True,
             legend=dict(font=dict(color='white')),
             xaxis=dict(
             title=dict(
             font=dict(
                  color='white'
             )
             ),
             tickfont=dict(
             color='white'
             )
             ),
             yaxis=dict(
             title=dict(
             font=dict(
                 color='white'
             )
             ),
             tickfont=dict(
             color='white'
             )
             ) ,dragmode=None)


             return fig




def convert(value):
    return str(value*100) + '%'

def get_style(**options):
        """Format the style"""

        style = {'position':'absolute'}
        #style = {'position':'relative'}

        if 'color' in options.keys(): style['color'] = options['color']
        #style.update({'position':'absolute'})

        if ('x' in options.keys()) and ('y' in options.keys()):
           """Infer manual mode""" 
           options['mode'] = 'manual' 

        if ('x' in options.keys()) and not ('y' in options.keys()):
           """Infer manual mode""" 
           options['mode'] = 'vCentered' 

        if not ('x' in options.keys()) and ('y' in options.keys()):
           """Infer manual mode""" 
           options['mode'] = 'hCentered' 

       

        mode = options.setdefault('mode','full')
        if mode == 'manual':
         style.update({'left'  :convert(options.setdefault('x',0))})
         style.update({'bottom':convert(options.setdefault('y',0))})

         if 'w' in options.keys():
             style.update({'width':convert(options['w'])})
            
         if 'h' in options.keys():
             style.update({'height':convert(options['h'])})
     
        elif mode == 'full':
          
               
            w =  options.setdefault('w',1)
            h =  options.setdefault('h',1)
            style['left']   = convert((1-w)/2)
            style['bottom'] = convert((1-w)/2)
            style['width']  = convert(w)
            style['height'] = convert(h)

        elif mode == 'hCentered':
            style['bottom'] = convert(options['y'])
            style['textAlign'] = 'center'
            style['alignItems']     = 'center'
            #This needs to be texted with other objects than text
            style['justifyContent'] = 'center'
            if 'w' in options.keys():
             style['width']   = convert(options['w'])

            if 'h' in options.keys():
             style['height']  = convert(options['h'])
            

        elif mode == 'vCentered':


            style['display']         = 'flex'
            style['alignItems']     = 'center'
            style['justifyContent'] = 'center'
            style['height']          = convert(options.setdefault('h',1))
            style['left']   = convert(options.setdefault('x',0))
            if 'w' in options.keys():
              style['width']   = convert(options['w'])

            
        if 'align' in options.keys():
            style['text-align'] = options['align']   
            style['transform']= "translateX(-50%)"

      
        return style

