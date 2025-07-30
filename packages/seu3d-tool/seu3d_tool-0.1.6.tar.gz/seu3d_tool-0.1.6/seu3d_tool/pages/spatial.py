#!/usr/bin/env python
# coding: utf-8

import dash
dash.register_page(__name__, path='/')

# In[] env
import math
from functools import reduce
from dash import dcc, html, dash_table, no_update, State, Patch, clientside_callback, ctx, ClientsideFunction
from dash import ALL, MATCH
from dash.dash_table.Format import Format
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import feffery_antd_components as fac
import feffery_utils_components as fuc
import dash_bootstrap_components as dbc
from dash_extensions.enrich import Output, Input, html, callback, Serverside
import plotly.express as px
import plotly.graph_objects as go
import scanpy as sc
import pandas as pd
import numpy as np
import squidpy as sq
from typing import List, Dict
import yaml
import pkg_resources
import os
import json


# In[] data

seu3d_dist = pkg_resources.get_distribution("seu3d-tool")
pkg_path = os.path.join(seu3d_dist.location, 'seu3d_tool')

with open(os.path.join(pkg_path, 'seu3d_config.yaml'), 'r') as f:
    config = yaml.safe_load(f)
    colormap = config['colormap']

dataset = {}
for stage, path in config['Dataset'].items():
    dataset[stage] = sc.read_h5ad(path)

coord_data = {}
for stage, adata in dataset.items():
  coord_data[stage] = pd.DataFrame(adata.obsm[config['3D_embedding']])
  if coord_data[stage].shape[1] != 3:
    raise ValueError('Not a 3D embedding!')
  coord_data[stage].columns = ['x', 'y', 'z']
  coord_data[stage].index = dataset[stage].obs_names


# In[] functions

def show_expViolin(adata, feature, **kws):
  data = adata[:,feature].to_df()[feature]
  # data = data[data>0]
  fig = go.Figure(
    data = go.Violin(
      x=data, y0=f'{feature}({len(data)})', line_color='black',
      fillcolor='lightseagreen', opacity=0.6,
      orientation='h', side='positive', width=1.5, **kws,
    )
  )
  
  fig.update_layout(
    plot_bgcolor = 'rgba(200,200,200,0.1)', showlegend=False
  ).update_yaxes(
    gridcolor='rgba(200,200,200,0.6)', gridwidth=1,
  ).update_xaxes(
    dtick=1, gridcolor='#ffffff', gridwidth=1, griddash='solid'
  )
  return fig

def show_ctpExpViolin(adata, feature, ctp_key: str = config['annotation'], **kws):
  pdf = pd.concat([adata[:,feature].to_df(), adata.obs[ctp_key]], axis=1)
  counts = pdf[ctp_key].value_counts()
  counts = counts[counts>0]
  sorted_ctp = counts.index.to_list()
  pdf[ctp_key] = pd.Categorical(pdf[ctp_key].to_list(),
                                   categories=sorted_ctp[::-1])
  fig = px.violin(
    pdf, x=feature, y=ctp_key, color = ctp_key, 
    color_discrete_map=colormap, orientation='h', height=800,
  ).update_traces(
    side='positive', width=1.5, **kws,
  ).update_layout(
    plot_bgcolor = 'rgba(200,200,200,0.1)',
  ).update_yaxes(
    gridcolor='rgba(200,200,200,0.6)', gridwidth=1,
  ).update_xaxes(
    dtick=1, gridcolor='#ffffff', gridwidth=1, griddash='solid'
  )
  return fig

def show_multiFeatures_expViolin(adata, features_dict, **kws):
  
  fig = go.Figure()
  
  filt_dict = {}
  for color,feature  in features_dict.items():
      if feature:
          filt_dict[color] = feature

  for color in list(filt_dict.keys())[::-1]:
    data = adata[:,filt_dict[color]].to_df()[filt_dict[color]]
    fig.add_trace(
      go.Violin(
        x=data, y0=f'{filt_dict[color]}({len(data)})', box_visible=False, 
        line_color='black', meanline_visible=False,
        fillcolor=color, opacity=0.6,
        orientation='h', side='positive', width=1.5, **kws, 
      )
    )
  fig.update_layout(
    plot_bgcolor = 'rgba(200,200,200,0.1)', showlegend=False
  ).update_yaxes(
    gridcolor='rgba(200,200,200,0.6)', gridwidth=1,
  ).update_xaxes(
    dtick=1, gridcolor='#ffffff', gridwidth=1, griddash='solid'
  )
  
  return fig

def show_multiFeatures_ctpExpViolin(adata, features_dict, ctp_key: str = config['annotation'], **kws):
  
  filt_dict = {}
  for color,feature  in features_dict.items():
      if feature:
          filt_dict[color] = feature
  features = list(filt_dict.values())

  pdf = pd.concat([adata[:,features].to_df(), adata.obs[ctp_key]], axis=1)
  pdf = pdf.melt(id_vars=ctp_key)
  pdf = pdf.rename(columns = {'variable': 'Gene', 'value': 'expression'})
  # pdf = pdf[pdf['expression']>0]

  pdf[ctp_key] = pd.Categorical(pdf[ctp_key], ordered=True)
  # counts = pdf.groupby('Gene').apply(lambda x: x.value_counts())

  fig = px.violin(
    pdf, x='expression', y=ctp_key, color = ctp_key, 
    color_discrete_map=colormap, orientation='h', height=800,
    animation_frame='Gene', 
  ).update_traces(
    side='positive', width=1.5, **kws,
  ).update_layout(
    plot_bgcolor = 'rgba(200,200,200,0.1)',
  ).update_yaxes(
    gridcolor='rgba(200,200,200,0.6)', gridwidth=1,
  ).update_xaxes(
    dtick=1, gridcolor='#ffffff', gridwidth=1, griddash='solid'
  )
    
  return fig

def vector_to_rgba(v):
  color = list(v.keys())
  color = [str(math.ceil(v[i])) if i in color else '244' for i in ['R', 'G', 'B'] ]
  if(all([ i=='244' for i in color])):
    rgba = 'rgba(244,244,244,1)'
  else:
    rgba = f'rgba({color[0]}, {color[1]}, {color[2]}, 1)'
    
  return rgba

def multiGenes_show_color(adata, genes_dict):
  tmp = {}
  for key,value  in genes_dict.items():
      if value:
          tmp[key] = value
  genes_dict = tmp
  colors = list(genes_dict.keys())
  others = [i for i in ['R', 'G', 'B'] if i not in colors]
  genes = list(genes_dict.values())

  exp = adata[:, genes].to_df()
  exp.columns = colors

  delta = exp.div(exp.max(axis=0), axis=1)*244
  delta[others] = 0

  def delta_geoMean(a,b):
    geoMean = np.sqrt((a**2+b**2)/2)
    # geoMean = ((a**3+b**3)/2)**(1/3)
    return geoMean
  def mean(a,b, c=None):
    if c:
      return (a+b+c)/3
    else:
      return (a+b)/2

  if len(colors)==1:
    color = pd.DataFrame({
        colors[0] : 244,
        others[0] : 244-delta[colors[0]],
        others[1] : 244-delta[colors[0]],
    })
  elif len(colors)==2:
    color = pd.DataFrame({
        colors[0] : 244-delta[colors[1]],
        colors[1] : 244-delta[colors[0]],
        others[0] : 244-delta_geoMean(delta[colors[1]],delta[colors[0]]),
    })
  elif len(colors)==3:
    color = pd.DataFrame({
        'R' : 244-delta_geoMean(delta['G'], delta['B']),
        'G' : 244-delta_geoMean(delta['R'], delta['B']),
        'B' : 244-delta_geoMean(delta['R'], delta['G']),
    })
  
  color['RGBA'] = color.apply(vector_to_rgba, axis=1)
  return color['RGBA']

def hex_to_rgbList(hex_color):
  hex_color = hex_color.replace(' ', '').replace('#', '')
  if len(hex_color) == 6:
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
  return [r,g,b]

def mix_multipy(color, alpha):

  def multipy(x,y):
    return x*y/255

  def mix(x, y):
    alpha = x[3]+y[3]-x[3]*y[3]
    if alpha==0:
      return [244,244,244, 0]
    else:
      R = np.round( (x[3]*(1-y[3])*x[0]+x[3]*y[3]*multipy(x[0],y[0])+(1-x[3])*y[3]*y[0])/alpha).astype(int)
      G = np.round( (x[3]*(1-y[3])*x[1]+x[3]*y[3]*multipy(x[1],y[1])+(1-x[3])*y[3]*y[1])/alpha).astype(int) 
      B = np.round( (x[3]*(1-y[3])*x[2]+x[3]*y[3]*multipy(x[2],y[2])+(1-x[3])*y[3]*y[2])/alpha).astype(int)
      return [R,G,B,alpha]

  array = []
  for c,a in zip(color, alpha):
    array.append(c.copy())
    array[-1].append(a)

  res = reduce(mix, array)
  res = f'rgb{res[0],res[1],res[2]}'

  return res

def color_mixer(adata, genes_dict):
  genes_dict_copy = genes_dict.copy()
  _ = [genes_dict_copy.pop(color) for color in genes_dict.keys() if not genes_dict[color]]
  colors = [hex_to_rgbList(c) for c in genes_dict_copy.keys()]
  genes = list(genes_dict_copy.values())
  
  exp = adata[:,genes].to_df()
  
  alpha = exp.div(exp.max(axis=0), axis=1)
  
  cell_colors = alpha.apply( axis=1, func=lambda row: mix_multipy(colors,row))
  
  return cell_colors

def cal_moran_3D(adata):
  tmp = adata.copy()
  sq.gr.spatial_neighbors(tmp, spatial_key='X_spatial')
  sq.gr.spatial_autocorr(tmp, mode='moran', n_jobs=1)
  df = tmp.uns['moranI'][['I']]
  df.columns = ["Moran's I"]
  return df

# In[] global vars

colorPicker_swatches = [
  "#25262b", "#868e96", "#fa5252", "#e64980", "#be4bdb", "#7950f2", "#4c6ef5",
  '#225ea8', "#228be6", "#15aabf", "#12b886", "#40c057", "#82c91e", "#fab005", "#fd7e14",
]

initColor_multiName = [
  "#fa5252", "#228be6", "#40c057", "#fd7e14", "#be4bdb", "#e64980", "#15aabf", "#fab005", "#868e96", 
]

config_scatter3d = {
  'toImageButtonOptions': {
    'format': 'png', # one of png, svg, jpeg, webp,
    'scale': 3
  }
} 

config_violin = {
  'toImageButtonOptions': {
    'format': 'png', # one of png, svg, jpeg, webp,
    'scale': 3
  }
}

# In[] app/widgets/3D:

SET_STORE_JSONtoPlot_3D = html.Div(
  [
    dcc.Store(data={}, id='STORE_obs_3D'),
    dcc.Store(data={}, id='STORE_cellsObsFilter_3D'),
    dcc.Store(data={}, id='STORE_cellsExpFilter_3D'),
    dcc.Store(data={}, id='STORE_singleExp_3D'),
    dcc.Store(data={}, id='STORE_multiExp_3D'),
    dcc.Store(data={}, id='STORE_mixedColor_3D'),
    dcc.Store(data=False, id='STORE_ifmulti_3D'),
    dcc.Store(data=colormap, id='STORE_ctpCmap_3D'),
    dcc.Store(id='STORE_cellsCtpFilter_3D'),
    dcc.Store(id='STORE_cellsIntersection_3D'),
    dcc.Store(id='test'),
  ]
)

init_range = dict(
  x_min = np.floor(coord_data[next(iter(dataset))]['x'].min()/10)*10, x_max = np.ceil(coord_data[next(iter(dataset))]['x'].max()/10)*10,
  y_min = np.floor(coord_data[next(iter(dataset))]['y'].min()/10)*10, y_max = np.ceil(coord_data[next(iter(dataset))]['y'].max()/10)*10,
  z_min = np.floor(coord_data[next(iter(dataset))]['z'].min()/10)*10, z_max = np.ceil(coord_data[next(iter(dataset))]['z'].max()/10)*10,
)

SET_STORE_Ranges_3D = html.Div(
  [
    dcc.Store(data = init_range, id='STORE_previewRange_3D'),
    dcc.Store(data = init_range, id='STORE_sliceRange_3D'),
    dcc.Store(data = init_range, id='STORE_maxRange_3D'),
  ]
)

def iconHover_colorPicker(init_color: str, id: Dict, swatches: List[str], placement='left', trigger='click'):
  return fac.AntdPopover(
    # openDelay=200,
    placement = placement,
    trigger= trigger,
    children=[
      dmc.ActionIcon(
        DashIconify(icon = 'fluent:circle-48-filled', color=init_color, width=48),
        variant='transparent', id=id['dmc_ActionIcon'], mt=3
      ),
    ],
    content = [
      dmc.ColorPicker(id=id['dmc_ColorPicker'], format='hex', value=init_color, swatches=swatches),
      dmc.TextInput(value=init_color, id=id['dmc_TextInput']),
    ]
  )

def drawerContent_ctpColorPicker(celltypes: List[str], cmap: Dict, swatches=colorPicker_swatches):
  stack = dmc.Stack(
    children=[
      dmc.Grid(
        gutter = 2,
        children=[
          dmc.Col(dmc.Text(ctp), span=10),
          dmc.Col(
            iconHover_colorPicker(
              id = {
                'dmc_ActionIcon': {'type': 'ACTIONICON_colorCtp_3D', 'id': ctp},
                'dmc_ColorPicker': {'type': 'COLORPICKER_colorCtp_3D', 'id': ctp},
                'dmc_TextInput': {'type': 'TEXT_colorCtp_3D', 'id': ctp},
              },  placement='right', init_color=cmap[ctp], swatches = [colormap[ctp]]+swatches
            ),
            span=2
          )
        ],
      )
      for ctp in celltypes
    ],
  )

  return stack

# In[] app/tabs/:

spatial_tab_plotFeature3D = dbc.Tab(
  [dmc.Grid([
    # options
    dmc.Col([
      fuc.FefferySticky([
        fac.AntdSpace(
          size=0,
          direction='vertical',
          className='fac-AntdSpace-sideBar',
          children=[
            # Select data
            fac.AntdCollapse(
              isOpen = True,
              forceRender = True,
              className = 'fac-AntdCollapse-sidebar',
              ghost=True,
              title = dmc.Text('Select data', className='dmc-Text-sidebar-title'),
              children = [
                dmc.Grid([
                  dmc.Col([
                    dbc.Label("Feature type"),
                    dcc.Dropdown(
                      # ['Gene', 'Regulon'],
                      ['Gene'],
                      'Gene',
                      id="DROPDOWN_featureType_3D",
                      clearable=False,
                      searchable=True,
                    ),
                  ], span=6, style={'visibility': 'collapse'},),
                  dmc.Col([
                    dbc.Label("Stage"),
                    dcc.Dropdown(
                      list(dataset.keys()),
                      next(iter(dataset)),
                      id="DROPDOWN_stage_3D",
                      clearable=False,
                      searchable=True,
                    ),
                  ], span=6),
                  dmc.Col(dmc.Text(id='TEXT_dataSummary_3D', color='gray'), span=12),
                ], gutter='xs'),
              ]
            ),
            # Plot options
            fac.AntdCollapse(
              isOpen = True,
              forceRender = True,
              className = 'fac-AntdCollapse-sidebar',
              ghost=True,
              title = dmc.Text('Plot options', className='dmc-Text-sidebar-title'),
              children = [          
                dmc.Tabs(
                  [
                    dmc.TabsList([
                      dmc.Tab('Settings', value='settings'),
                      dmc.Tab('Single', value='single'),
                      dmc.Tab('Multiple', value='multi'),
                    ], grow=True),
                    # settings
                    dmc.TabsPanel(
                      [
                        dmc.Tabs(
                          [
                            dmc.TabsList([
                              dmc.Tab('Scatter-3D', value='Scatter-3D'),
                              dmc.Tab('Violin', value='Violin')
                            ], grow=False),
                            # scatter-3d
                            dmc.TabsPanel(
                              [
                                
                                dmc.Divider(label = 'Points', labelPosition='center', variant='dashed', className='dmc-divider-sidebar-inline'),
                                dmc.Grid([
                                  dmc.Col(dmc.Text('Point size:', className='dmc-Text-label'), span=5),
                                  dmc.Col(dmc.NumberInput(
                                    value=3, step=0.5, min=0.1, id='NUMBERINPUT_scatter3dPointsize_3D', precision=1,
                                    persistence = True, persistence_type = 'local'
                                  ), span=7),
                                ], justify='center', gutter=3, className='dmc-Grid-center'),
                                dmc.Space(h=5),

                                dmc.Switch(label='Hide non-expressing cells', id='SWITCH_hideZero_3D',  size='md',
                                          onLabel=DashIconify(icon='solar:eye-closed-linear', width=14), 
                                          offLabel=DashIconify(icon='solar:eye-linear', width=14),
                                          persistence = False, persistence_type = 'local'),
                                dmc.Space(h=5),
                                
                                dmc.Divider(label = 'Axes', labelPosition='center', variant='dashed', className='dmc-divider-sidebar-inline'),
                                dmc.Text('Projection type:', className='dmc-Text-label'),
                                dmc.SegmentedControl(
                                  value='orthographic', 
                                  data=[
                                    {'value': 'perspective', 'label': 'Perspective'},
                                    {'value': 'orthographic', 'label': 'Orthographic'},
                                  ], 
                                  fullWidth=True, id='SEGMENTEDCONTROL_projection_3D',
                                  persistence = True, persistence_type = 'local',
                                ),
                                dmc.Space(h=5),
                                dmc.Switch(label='Hide axes', id='SWITCH_hideAxes_3D', size='md',
                                  onLabel=DashIconify(icon='solar:eye-closed-linear', width=14), 
                                  offLabel=DashIconify(icon='solar:eye-linear', width=14),
                                  persistence = True, persistence_type = 'local'),
                                
                                dmc.Divider(label='Download', labelPosition='center', variant='dashed', className='dmc-divider-sidebar-inline'),
                                dmc.Text('tip: replot to take effect', className='dmc-Text-sidebar-tips'),
                                dmc.Grid([
                                  dmc.Col(dmc.Select( label = 'type', id='NUMBERINPUT_scatter3dFigtype_3D',
                                    value='png', data = ['svg', 'png', 'jpeg', 'webp'],
                                    persistence = True, persistence_type = 'local', 
                                  ), span=6),
                                  dmc.Col(dmc.NumberInput( label = 'scale(resolution)', id='NUMBERINPUT_scatter3dFigscale_3D',
                                    value=3, step=1, min=1, icon=DashIconify(icon='uim:multiply', width=16),
                                    persistence = True, persistence_type = 'local', 
                                  ), span=6),
                                ], justify='center', gutter=3, className='dmc-Grid-center'),
                              ],
                              value = 'Scatter-3D'
                            ),
                            # violin
                            dmc.TabsPanel(
                              [
                                dmc.Divider(label = 'Points', labelPosition='center', variant='dashed', className='dmc-divider-sidebar-inline'),
                                dmc.SegmentedControl(
                                  value='outliers',
                                  data = [
                                    {'value': 'none', 'label': 'none'},
                                    {'value': 'outliers', 'label': 'outliers'},
                                    {'value': 'all', 'label': 'all'}
                                  ],
                                  fullWidth=True, id='SEGMENTEDCONTROL_violinPoints_3D',
                                  persistence = True, persistence_type = 'local',
                                ),
                                dmc.Grid(
                                  [
                                    dmc.Col(dmc.NumberInput(label='position', value=0, step=0.1, min=-2, max=2, 
                                                    id='NUMBERINPUT_violinPointpos_3D', precision=2,
                                                    persistence = True, persistence_type = 'local',), span=4),
                                    dmc.Col(dmc.NumberInput(label='size', value=2.5, step=0.5, min=0, max=10,
                                                    id='NUMBERINPUT_violinPointsize_3D', precision=1,
                                                    persistence = True, persistence_type = 'local',), span=4),
                                    dmc.Col(dmc.NumberInput(label='jitter', value=0.15, step=0.05, min=0, max=1,
                                                    id='NUMBERINPUT_violinPointjitter_3D', precision=2,
                                                    persistence = True, persistence_type = 'local',), span=4),
                                  ],
                                ),
                                dmc.Divider(label = 'Box', labelPosition='center', variant='dashed', className='dmc-divider-sidebar-inline'),
                                dmc.SegmentedControl(
                                  value='all',
                                  data = [
                                    {'value': 'none', 'label': 'none'},
                                    {'value': 'box', 'label': 'box'},
                                    {'value': 'meanline', 'label': 'mean'},
                                    {'value': 'all', 'label': 'all'}
                                  ],
                                  id='SEGMENTEDCONTROL_violinBox_3D', fullWidth=True,
                                  persistence = True, persistence_type = 'local',
                                ),
                                dmc.NumberInput(label='Box width', value=0.5, step=0.1, min=0, max=1,
                                                id='NUMBERINPUT_violinBoxwidth_3D', precision=1,
                                                persistence = True, persistence_type = 'local',),
                                
                                dmc.Divider(label='Download', labelPosition='center', variant='dashed', className='dmc-divider-sidebar-inline'),
                                dmc.Text('tip: replot to take effect', className='dmc-Text-sidebar-tips'),
                                dmc.Grid([
                                  dmc.Col(dmc.Select( label = 'type', id='NUMBERINPUT_violinFigtype_3D',
                                    value='png', data = ['svg', 'png', 'jpeg', 'webp'],
                                    persistence = True, persistence_type = 'local', 
                                  ), span=6),
                                  dmc.Col(dmc.NumberInput( label = 'scale(resolution)', id='NUMBERINPUT_violinFigscale_3D',
                                    value=3, step=1, min=1, icon=DashIconify(icon='uim:multiply', width=16),
                                    persistence = True, persistence_type = 'local', 
                                  ), span=6),
                                ], justify='center', gutter=3, className='dmc-Grid-center'),
                              ],
                              value = 'Violin'
                            ),
                          ],
                          value = 'Scatter-3D',
                          variant = 'pills',
                          color = 'grape'
                        ),
                      ],
                      value = 'settings',
                    ),
                    # single
                    dmc.TabsPanel(
                      [
                        dmc.Grid([
                          dmc.Col([
                            dcc.Dropdown(
                              options = dataset[next(iter(dataset))].var_names,
                              value = dataset[next(iter(dataset))].var_names[0],
                              id="DROPDOWN_singleName_3D",
                              clearable=False
                            ),
                          ], span=10),
                          dmc.Col([
                            iconHover_colorPicker(
                              id={
                                'dmc_ActionIcon': 'ACTIONICON_colorSingle_3D', 
                                'dmc_ColorPicker': 'COLORPICKER_single_3D', 
                                'dmc_TextInput': 'TEXT_colorSingle_3D',
                                },
                              init_color='#225ea8', swatches=colorPicker_swatches,
                            )
                          ], span=2),
                          dmc.Col([
                            dmc.Button('Plot', id='BUTTON_singlePlot_3D', color='dark', fullWidth=True,
                                      leftIcon=DashIconify(icon="gis:cube-3d", width=24)),
                          ], span=12),
                        ], gutter='xs')  
                      ],
                      value='single',
                    ),
                    # multi
                    dmc.TabsPanel(
                      [
                        # extendable selector
                        html.Div(
                          [
                            dmc.Grid([
                              dmc.Col(dcc.Dropdown(options = [], id={'type': 'DROPDOWN_multiName_3D', 'index': 0}), span=10),
                              dmc.Col(
                                iconHover_colorPicker(
                                  id={
                                    'dmc_ActionIcon': {'type':'ACTIONICON_colorMulti_3D', 'index': 0}, 
                                    'dmc_ColorPicker': {'type': 'COLORPICKER_multi_3D', 'index': 0}, 
                                    'dmc_TextInput': {'type': 'TEXT_colorMulti_3D', 'index': 0},
                                    },
                                  init_color=initColor_multiName[0], swatches=colorPicker_swatches,
                                ),
                                span=2
                              ),
                            ]),
                            dmc.Grid([
                              dmc.Col(dcc.Dropdown(options = [], id={'type': 'DROPDOWN_multiName_3D', 'index': 1}), span=10),
                              dmc.Col(
                                iconHover_colorPicker(
                                  id={
                                    'dmc_ActionIcon': {'type':'ACTIONICON_colorMulti_3D', 'index': 1}, 
                                    'dmc_ColorPicker': {'type': 'COLORPICKER_multi_3D', 'index': 1}, 
                                    'dmc_TextInput': {'type': 'TEXT_colorMulti_3D', 'index': 1},
                                    },
                                  init_color=initColor_multiName[1], swatches=colorPicker_swatches,
                                ),
                                span=2
                              ),
                            ]),
                          ],
                          id = 'DIV_multiNameDynamic_3D',
                        ),
                        dcc.Store(data=2, id='STORE_multiNameCurNumber'),
                        # buttons
                        dmc.Grid(
                          [
                            dmc.Col(dmc.Button(
                              'Add', id='BUTTON_addFeature_3D', color='teal', fullWidth=True,
                              leftIcon=DashIconify(icon="fluent:add-square-20-regular", width=20)
                            ), span=23),
                            dmc.Col(dmc.Button(
                              'Delete', id='BUTTON_deleteFeature_3D', color='red', fullWidth=True,
                              leftIcon=DashIconify(icon="fluent:subtract-square-20-regular", width=20)
                            ), span=27),
                            dmc.Col(dmc.Button(
                              'Plot', id='BUTTON_multiPlot_3D', color='dark', fullWidth=True,
                              leftIcon=DashIconify(icon="gis:cube-3d", width=24),
                            ), span=50),
                          ],
                          columns=50,
                        ),
                        dcc.Store(id='STORE_multiNameInfo_3D'),
                      ],
                      value='multi',
                    ),
                  ], 
                  orientation = 'horizontal',
                  className = 'dmc-Tabs-inline',
                  # variant = 'pills',
                  value = 'single',
                ),
              ]
            ),
            # Slicer
            fac.AntdCollapse(
              isOpen = False,
              forceRender = True,
              className = 'fac-AntdCollapse-sidebar',
              ghost=True,
              title = dmc.Text('Slicer', className='dmc-Text-sidebar-title'),
              children = [
                dmc.Grid([
                  dmc.Col(dmc.Text('x', className='.dmc-Text-label-center'), span=2),
                  dmc.Col(
                    dcc.RangeSlider(
                      step=10, id='SLIDER_Xrange_3D',
                      marks=None, tooltip={'placement': 'bottom', 'always_visible': True}
                    ),
                    span=10
                  ),
                  dmc.Col(dmc.Text('y', className='.dmc-Text-label-center'), span=2),
                  dmc.Col(
                    dcc.RangeSlider(
                      step=10, id='SLIDER_Yrange_3D',
                      marks=None, tooltip={'placement': 'bottom', 'always_visible': True}
                    ),
                    span=10
                  ),
                  dmc.Col(dmc.Text('z', className='.dmc-Text-label-center'), span=2),
                  dmc.Col(
                    dcc.RangeSlider(
                      step=10, id='SLIDER_Zrange_3D',
                      marks=None, tooltip={'placement': 'bottom', 'always_visible': True}
                    ),
                    span=10
                  ),
                  dmc.Col(
                    dmc.Switch(size='md', id='SWITCH_previewBox_3D', label='Preview', checked=False),
                    span=12
                  ),
                  dmc.Col(
                    dmc.Button(
                      'Slice', color='red', id='BUTTON_slice_3D', fullWidth=True, 
                      leftIcon=DashIconify(icon='fluent:screen-cut-20-regular', width=20),
                    ),
                    span=6
                  ),
                  dmc.Col(
                    dmc.Button(
                      'Recover', color='teal', id='BUTTON_recover_3D', fullWidth=True, 
                      leftIcon=DashIconify(icon='fluent:arrow-sync-circle-20-regular', width=20),
                    ),
                    span=6
                  )
                ]),
                SET_STORE_Ranges_3D,
              ],
            ),
            # Moran
            fac.AntdCollapse(
              isOpen = False,
              forceRender = True,
              className = 'fac-AntdCollapse-sidebar',
              ghost=True,
              title = dmc.Text('Compute SVG(moran)', className='dmc-Text-sidebar-title'),
              children = [
                dmc.Grid([
                  dmc.Col(
                    dmc.Button('Compute', id='BUTTON_calMoran_3D', color='dark', fullWidth=True,
                        leftIcon = DashIconify(icon='fluent:clipboard-math-formula-20-regular', width=20) ),
                    span=6,
                  ),
                  dmc.Col(
                    dmc.Button('Result', id='BUTTON_showMoran_3D', fullWidth=True,
                        leftIcon = DashIconify(icon='fluent:clipboard-checkmark-20-regular', width=20) ),
                    span=6,
                  ),
                  dmc.Text('Using current cells to compute SVGs', className='dmc-Text-sidebar-tips'),
                ]),
                dbc.Offcanvas(
                  [dash_table.DataTable(
                    id='DATATABLE_moranRes_3D',
                    sort_action="native", page_action='native', filter_action="native",
                    page_current= 0, page_size= 20, fill_width=True,
                    style_cell={'textAlign': 'center'},
                    style_table={'overflowX': 'auto'},
                  )],
                  title = 'SVGs:',
                  placement='end', scrollable=True, backdrop=False, is_open=False,
                  id = 'OFFCANVAS_moranRes_3D',
                ),
              ],
            ),
            # tmp-Angle
            fac.AntdCollapse(
              isOpen=False,
              forceRender=True,
              ghost=True,
              title = dmc.Text('Camera Angle', className='dmc-Text-sidebar-title'),
              children = dmc.Stack(
                [
                  dmc.Group([
                    html.Pre(id = 'PRE_camera_angle_3D'),
                  ]),
                  dmc.Group([
                    dmc.Button('Get angle', id='BUTTON_get_angle_3D'),
                    dmc.Button('Set angle', id='BUTTON_set_angle_3D'),
                  ])
                ]
              )
            )
          ],
        ),
      ], top=10),
    ], span=9),
    # viewer
    dmc.Col([
      SET_STORE_JSONtoPlot_3D,
      # scatter3d
      dmc.Grid([
        dmc.Col([
          dcc.Graph(figure={}, id="FIGURE_3Dexpression", 
                    className='dcc-Graph-scatter3d', config=config_scatter3d),
        ], span=20),
        dmc.Col([
          dcc.Graph(figure={}, id="FIGURE_3Dcelltype",
                    className='dcc-Graph-scatter3d', config=config_scatter3d),
        ], span=20),
        dmc.Col([
          # DIY-legend
          dmc.Grid([
            # set colors
            dmc.Col(dmc.Button(
              'Setting Colors', variant="gradient", gradient={"from": "grape", "to": "pink", "deg": 35},
              id='BUTTON_setColors_3D', fullWidth=True,
              leftIcon=DashIconify(icon='fluent:color-20-regular', width=20)
            ), span=12),
            # invert selection
            dmc.Col(
              dmc.Button(
                DashIconify(icon='system-uicons:reverse', width=21), variant='light', color='gray',
                id='BUTTON_invertSelectionCtp_3D', fullWidth=True,),
              span=4),
            # clear selection
            dmc.Col(dmc.Button(
              DashIconify(icon='fluent:border-none-20-regular', width=20), variant="light", color='gray',
              id='BUTTON_clearSelectionCtp_3D', fullWidth=True,
            ), span=4),
            # all selection
            dmc.Col(dmc.Button(
              DashIconify(icon='fluent:checkbox-indeterminate-20-regular', width=20), variant="light", color='gray',
              id='BUTTON_allSelectionCtp_3D', fullWidth=True,
            ), span=4),
          ], gutter=2),
          # tooltips for buttons
          html.Div(
            [
              dbc.Tooltip( i.capitalize(), target=f'BUTTON_{i}SelectionCtp_3D', placement='top')
              for i in ['invert', 'clear', 'all']
            ],
          ),
          dmc.ChipGroup(
            children=[], value=[], multiple=True, align='center', spacing=1, 
            id = 'CHIPGROUP_celltype_3D', className='dmc-ChipGroup-legend'
          ),
          dcc.Store(id='STORE_allCelltypes_3D'),
          fac.AntdDrawer(
            children=[], id='DRAWER_setColorCtp_3D',
            title=dmc.Stack([
              dmc.Text('Setting colors', className='dmc-Text-drawerTitle'),
              dmc.Text("tip: colors will be saved locally", className='dmc-Text-drawerSubTitle')
            ], spacing=1),
            width=300,
          )
        ], span=10)
      ], columns=50),
      # violin
      dbc.Row([
        dbc.Col([
          dbc.Label( 'Normalized expression in all celltypes(left)'),
          dbc.Label('and in each celltype(right):'),
          dcc.Graph(figure={}, id="FIGURE_expViolin_3D", className='dcc-Graph-violin-exp', config=config_violin)
        ], align='center', width=4),
        dbc.Col([
          dcc.Graph(figure={}, id="FIGURE_ctpViolin_3D", className='dcc-Graph-violin-ctp', config=config_violin)
        ], align='center', width=8)
      ], style={'overflow-y': 'auto'}, id='test_sticky')
    ],span=41),
  ], columns=50)],
  label = "Plot feature(3D)",
  tab_id = "spatial_tab_plotFeature3D",
)

spatial_tabs = dbc.Card(
  dbc.Tabs(
    [
      spatial_tab_plotFeature3D, 
    ],
    active_tab = "spatial_tab_plotFeature3D",  
    id = "spatial_tabs",
  ),
)

# In[] callbacks/3D:

# download scale
@callback(
  Output('FIGURE_3Dcelltype', 'config'),
  Output('FIGURE_3Dexpression', 'config'),
  Input('NUMBERINPUT_scatter3dFigtype_3D', 'value'),
  Input('NUMBERINPUT_scatter3dFigscale_3D', 'value'),
)
def update_scatter3dDownloadConfig_3D(type, scale):
  
  patch=Patch()
  patch['toImageButtonOptions']['format'] = type
  patch['toImageButtonOptions']['scale'] = scale
  
  return patch, patch

@callback(
  Output('FIGURE_expViolin_3D', 'config'),
  Output('FIGURE_ctpViolin_3D', 'config'),
  Input('NUMBERINPUT_violinFigtype_3D', 'value'),
  Input('NUMBERINPUT_violinFigscale_3D', 'value'),
)
def update_violinDownloadConfig_3D(type, scale):
  
  patch=Patch()
  patch['toImageButtonOptions']['format'] = type
  patch['toImageButtonOptions']['scale'] = scale
  
  return patch, patch

# violin options hot-update
@callback(
  Output('FIGURE_expViolin_3D', 'figure'),
  Output('FIGURE_ctpViolin_3D', 'figure'),
  Input('SEGMENTEDCONTROL_violinPoints_3D', 'value'),
  State('STORE_allCelltypes_3D', 'data'),
  State('STORE_multiNameInfo_3D', 'data'),
  prevent_initial_call=True
)
def update_violinPointStyle_3D(points, allCelltypes, minfo):
  
  points = False if points=='none' else points
  
  n_gene = len(minfo)
  n_ctp = len(allCelltypes)
  
  patch = Patch()
  for i in range(0, max(n_gene, n_ctp)):
    patch['data'][i]['points'] = points

  return patch, patch

@callback(
  Output('FIGURE_expViolin_3D', 'figure'),
  Output('FIGURE_ctpViolin_3D', 'figure'),
  Input('NUMBERINPUT_violinPointpos_3D', 'value'),
  State('STORE_allCelltypes_3D', 'data'),
  State('STORE_multiNameInfo_3D', 'data'),
  prevent_initial_call=True
)
def update_violinPointpos_3D(pointpos, allCelltypes, minfo):
  
  n_gene = len(minfo)
  n_ctp = len(allCelltypes)
  
  patch = Patch()
  for i in range(0, max(n_gene, n_ctp)):
    patch['data'][i]['pointpos'] = pointpos

  return patch, patch

@callback(
  Output('FIGURE_expViolin_3D', 'figure'),
  Output('FIGURE_ctpViolin_3D', 'figure'),
  Input('NUMBERINPUT_violinPointsize_3D', 'value'),
  State('STORE_allCelltypes_3D', 'data'),
  State('STORE_multiNameInfo_3D', 'data'),
  prevent_initial_call=True
)
def update_violinPointsize_3D(pointsize, allCelltypes, minfo):
  
  n_gene = len(minfo)
  n_ctp = len(allCelltypes)
  
  patch = Patch()
  for i in range(0, max(n_gene, n_ctp)):
    patch['data'][i]['marker']['size'] = pointsize

  return patch, patch

@callback(
  Output('FIGURE_expViolin_3D', 'figure'),
  Output('FIGURE_ctpViolin_3D', 'figure'),
  Input('SEGMENTEDCONTROL_violinBox_3D', 'value'),
  State('STORE_allCelltypes_3D', 'data'),
  State('STORE_multiNameInfo_3D', 'data'),
  prevent_initial_call=True
)
def update_violinBox_3D(box, allCelltypes, minfo):
  
  n_gene = len(minfo)
  n_ctp = len(allCelltypes)
  
  box_visible = True if box=='box' or box=='all' else False
  meanline_visible = True if box=='meanline' or box=='all' else False
  
  patch = Patch()
  for i in range(0, max(n_gene, n_ctp)):
    patch['data'][i]['box']['visible'] = box_visible
    patch['data'][i]['meanline']['visible'] = meanline_visible

  return patch, patch

@callback(
  Output('FIGURE_expViolin_3D', 'figure'),
  Output('FIGURE_ctpViolin_3D', 'figure'),
  Input('NUMBERINPUT_violinPointjitter_3D', 'value'),
  State('STORE_allCelltypes_3D', 'data'),
  State('STORE_multiNameInfo_3D', 'data'),
  prevent_initial_call=True
)
def update_violinPointJitter_3D(jitter, allCelltypes, minfo):
  
  n_gene = len(minfo)
  n_ctp = len(allCelltypes)
  
  patch = Patch()
  for i in range(0, max(n_gene, n_ctp)):
    patch['data'][i]['jitter'] = jitter

  return patch, patch

@callback(
  Output('FIGURE_expViolin_3D', 'figure'),
  Output('FIGURE_ctpViolin_3D', 'figure'),
  Input('NUMBERINPUT_violinBoxwidth_3D', 'value'),
  State('STORE_allCelltypes_3D', 'data'),
  State('STORE_multiNameInfo_3D', 'data'),
  prevent_initial_call=True
)
def update_violinBoxWidth_3D(boxwidth, allCelltypes, minfo):
  
  n_gene = len(minfo)
  n_ctp = len(allCelltypes)
  
  patch = Patch()
  for i in range(0, max(n_gene, n_ctp)):
    patch['data'][i]['box']['width'] = boxwidth

  return patch, patch

# update_dataSummary
@callback(
  Output('TEXT_dataSummary_3D', 'children'),
  Input('DROPDOWN_featureType_3D', 'value'),
  Input('DROPDOWN_stage_3D', 'value')
)
def update_dataSummary_3D(featureType, stage):
    
  str = f'{dataset[stage].shape[0]}(cells) × {dataset[stage].shape[1]}(features)'
  return str

# update_nameOptions
@callback(
  Output('DROPDOWN_singleName_3D', 'options'),
  Output('DROPDOWN_singleName_3D', 'value'),
  Input('DROPDOWN_singleName_3D', 'search_value'),
  Input('DROPDOWN_stage_3D', 'value'),
  prevent_initial_call=True
)
def update_nameOptions_single_3D(search, stage):

  tid = ctx.triggered_id

  if 'DROPDOWN_singleName_3D':
    if not search:
      opts = dataset[stage].var_names
    else:
      opts = dataset[stage].var_names[dataset[stage].var_names.str.startswith(search)].sort_values()
    value = no_update
  
  if tid == 'DROPDOWN_stage_3D':
    opts = dataset[stage].var_names
    value = opts[0]
  
  return opts, value

@callback(
  Output({'type': 'DROPDOWN_multiName_3D', 'index': MATCH}, 'options'),
  Input({'type': 'DROPDOWN_multiName_3D', 'index': MATCH}, 'search_value'),
  Input('DROPDOWN_featureType_3D', 'value'),
  Input('DROPDOWN_stage_3D', 'value'),
  prevent_initial_call=True,
)
def update_nameOptions_multi_3D(search, featureType, stage):
  
  if not search:
    opts = dataset[stage].var_names
  else:
    opts = dataset[stage].var_names[dataset[stage].var_names.str.startswith(search)].sort_values()
  
  return opts

# add & delte components for multiName
@callback(
  Output('DIV_multiNameDynamic_3D', 'children'),
  Output('STORE_multiNameCurNumber', 'data'),
  Input('BUTTON_addFeature_3D', 'n_clicks'),
  Input('BUTTON_deleteFeature_3D', 'n_clicks'),
  State('STORE_multiNameCurNumber', 'data'),
  State('DROPDOWN_featureType_3D', 'value'),
  State('DROPDOWN_stage_3D', 'value'),
  prevent_initial_call = True,
)
def add_components_multiName_3D(add, delete, curNumber, featureType, stage):

  id = ctx.triggered_id

  nextIndex = curNumber
  nextColor = initColor_multiName[int(nextIndex % len(initColor_multiName))]
  
  patch_children = Patch()
  if 'BUTTON_addFeature_3D' in id:
    patch_children.append(
      dmc.Grid([
        dmc.Col(dcc.Dropdown(options = [], id={'type': 'DROPDOWN_multiName_3D', 'index': nextIndex}), span=10),
        dmc.Col(
          iconHover_colorPicker(
            id={
              'dmc_ActionIcon': {'type':'ACTIONICON_colorMulti_3D', 'index': nextIndex}, 
              'dmc_ColorPicker': {'type': 'COLORPICKER_multi_3D', 'index': nextIndex}, 
              'dmc_TextInput': {'type': 'TEXT_colorMulti_3D', 'index': nextIndex},
              },
            init_color=nextColor, swatches=colorPicker_swatches,
          ),
          span=2
        ),
      ])
    )
    nextNumber = curNumber+1
  elif 'BUTTON_deleteFeature_3D' in id:
    if nextIndex >= 3 :
      del patch_children[nextIndex-1]
      nextNumber = curNumber-1 if curNumber>0 else 0
    else:
      nextNumber = curNumber

  return patch_children, nextNumber

# store_previewRange
clientside_callback(
  ClientsideFunction(
    namespace='plotFunc_3Dtab',
    function_name='store_previewRange',
  ),
  Output('STORE_previewRange_3D', 'data'),
  Input('SLIDER_Xrange_3D', 'value'),
  Input('SLIDER_Yrange_3D', 'value'),
  Input('SLIDER_Zrange_3D', 'value'),
)

# store_sliceRange
clientside_callback(
  ClientsideFunction(
    namespace='plotFunc_3Dtab',
    function_name='store_sliceRange'),
  Output('STORE_sliceRange_3D', 'data'),
  Input('BUTTON_slice_3D', 'n_clicks'),
  Input('BUTTON_recover_3D', 'n_clicks'),
  Input('STORE_maxRange_3D', 'data'),
  State('STORE_previewRange_3D', 'data'),
)

# max range
@callback(
  Output('STORE_maxRange_3D', 'data'),
  Input('DROPDOWN_stage_3D', 'value'),
)
def update_maxRange_3D(stage):
  obs = coord_data[stage]
  maxRange = dict(
    x_min = np.floor(obs.x.min()/10)*10, x_max = np.ceil(obs.x.max()/10)*10,
    y_min = np.floor(obs.y.min()/10)*10, y_max = np.ceil(obs.y.max()/10)*10,
    z_min = np.floor(obs.z.min()/10)*10, z_max = np.ceil(obs.z.max()/10)*10,
  )
  return maxRange

@callback(
  output=[
    ( Output('SLIDER_Xrange_3D', 'min'), Output('SLIDER_Xrange_3D', 'max'), Output('SLIDER_Xrange_3D', 'value') ),
    ( Output('SLIDER_Yrange_3D', 'min'), Output('SLIDER_Yrange_3D', 'max'), Output('SLIDER_Yrange_3D', 'value') ),
    ( Output('SLIDER_Zrange_3D', 'min'), Output('SLIDER_Zrange_3D', 'max'), Output('SLIDER_Zrange_3D', 'value') ),
  ],
  inputs = Input('STORE_maxRange_3D', 'data'),
)
def update_sliderRange_3D(maxRange):
  res = [
    ( maxRange[f'{c}_min'], maxRange[f'{c}_max'], (maxRange[f'{c}_min'], maxRange[f'{c}_max']) )
    for c in ['x', 'y', 'z']
  ]
  return  res

# store cells obsinfo forJSONtoPlot
@callback(
  Output('STORE_obs_3D', 'data'),
  Input('DROPDOWN_stage_3D', 'value'),
  Input('DROPDOWN_featureType_3D', 'value'),
)
def store_cellsObs_forJSONtoPlot_3D(stage, featureType):

  obs = pd.concat([ coord_data[stage], dataset[stage].obs[config['annotation']].astype(str) ], axis=1)
  return obs.to_dict('index')

@callback(
  Output('STORE_cellsObsFilter_3D', 'data'),
  
  Input('STORE_sliceRange_3D', 'data'),
  # Input('CHIPGROUP_germLayer_3D', 'value'),
  Input('DROPDOWN_stage_3D', 'value'),
  Input('DROPDOWN_featureType_3D', 'value'),
)
def store_cellsInfo_forJSONtoPlot_3D(sliceRange, stage, featureType):
  
  obs = pd.concat([coord_data[stage], dataset[stage].obs[config['annotation']].astype(str) ], axis=1)

  if_inSliceRange = ( 
                      (obs['x'] <= sliceRange['x_max']) & 
                      (obs['x'] >= sliceRange['x_min']) & 
                      (obs['y'] <= sliceRange['y_max']) & 
                      (obs['y'] >= sliceRange['y_min']) & 
                      (obs['z'] <= sliceRange['z_max']) & 
                      (obs['z'] >= sliceRange['z_min'])
                    )
  
  # if len(germs) >= 1:
  #   if_ingerms = [ True if i in germs else False for i in obs['germ_layer'] ]
  # else:
  #   raise PreventUpdate
  # obsnames_filt = dataset[stage].obs_names[if_inSliceRange & if_ingerms]
  obsnames_filt = dataset[stage].obs_names[if_inSliceRange]
  return Serverside(obsnames_filt)

# store_expInfo_forJSONtoPlot (download: <0.43M,<80ms; compute 320ms)
@callback(
  Output('STORE_cellsExpFilter_3D', 'data'),
  Output('STORE_singleExp_3D', 'data'),
  Output('STORE_multiExp_3D', 'data'),
  Output('STORE_ifmulti_3D', 'data'),
  Output('STORE_mixedColor_3D', 'data'),
  
  Input('BUTTON_singlePlot_3D', 'n_clicks'),
  Input('BUTTON_multiPlot_3D', 'n_clicks'),
  Input('SWITCH_hideZero_3D', 'checked'),
  Input('DROPDOWN_stage_3D', 'value'),
  
  Input('DROPDOWN_singleName_3D', 'value'), # use `Input` to wait for updating when `stage` changed
  State('STORE_multiNameInfo_3D', 'data'),
  State('STORE_ifmulti_3D', 'data'),
)
def store_expInfo_forJSONtoPlot_3D(sclick, mclick, hideZero, stage, sname, minfo, ifmulti):

  def return_single():
    ifmulti = False
    exp = dataset[stage][:,sname].to_df()
    if hideZero:
      cellsExpFilter = exp[(exp>0)[sname]].index
    else:
      cellsExpFilter = exp.index
    exp = exp.loc[cellsExpFilter,:]
    cellsExpFilter = cellsExpFilter.to_list()
    return (ifmulti, exp, cellsExpFilter)
  
  def return_multi():
    ifmulti = True
    mixColor = color_mixer(dataset[stage], minfo)
    if hideZero:
      cellsExpFilter = mixColor[mixColor!='rgb(244, 244, 244)'].index
    else:
      cellsExpFilter = mixColor.index
    mixColor = mixColor[cellsExpFilter]
    cellsExpFilter = cellsExpFilter.to_list()
    return (ifmulti, [], cellsExpFilter, mixColor.to_dict()) 
  
  def return_multiExp():
    tmp = {}
    for key,value in minfo.items():
      if value:
        tmp[key] = value
    colors = list(tmp.keys())
    genes = list(tmp.values())

    exp = dataset[stage][:, genes].to_df()
    exp.columns = colors
    exp = exp.to_dict('index')

    return exp
  
  btn_id = ctx.triggered_id
  if btn_id:
  
    if 'DROPDOWN_stage_3D' in btn_id:
      if not ifmulti:
        ifmulti,exp,cellsExpFilter = return_single()
        exp = exp.to_dict('index')
        return (Serverside(cellsExpFilter), exp, no_update, ifmulti, no_update)
      else:
        ifmulti,_,cellsExpFilter,mixcolor = return_multi()
        exp_multi = return_multiExp()
        return (Serverside(cellsExpFilter), no_update, exp_multi, ifmulti, mixcolor)

    elif 'BUTTON_singlePlot_3D' in btn_id:
      ifmulti,exp,cellsExpFilter = return_single()
      exp = exp.to_dict('index')
      if hideZero:
        return (Serverside(cellsExpFilter), exp, no_update, ifmulti, no_update)
      else:
        return (no_update, exp, no_update, ifmulti, no_update)
    
    elif 'BUTTON_multiPlot_3D' in btn_id:
      ifmulti,_,cellsExpFilter,mixcolor = return_multi()
      exp_multi = return_multiExp()
      if hideZero:
        return (Serverside(cellsExpFilter), no_update, exp_multi, ifmulti, mixcolor)
      else:
        return (no_update, no_update, exp_multi, ifmulti, mixcolor)
    
    elif 'SWITCH_hideZero_3D' in btn_id:
      
      if not hideZero:
        cellsExpFilter = dataset[stage].obs_names.to_list()
        return (Serverside(cellsExpFilter), no_update, no_update, no_update, no_update)
      
      else:
        if not ifmulti:
          _,_,cellsExpFilter = return_single()
          return (Serverside(cellsExpFilter), no_update, no_update, no_update, no_update)
        else:
          _,_,cellsExpFilter,_ = return_multi()
          exp_multi = return_multiExp()
          return (Serverside(cellsExpFilter), no_update, exp_multi, no_update, no_update)
        
    else:
      raise PreventUpdate

  else:
      ifmulti,exp,cellsExpFilter = return_single()
      exp = exp.to_dict('index')
      return (Serverside(cellsExpFilter), exp, no_update, ifmulti, no_update)

# update ChipGroup-celltype chips
@callback(
  Output('CHIPGROUP_celltype_3D', 'children'),
  Output('CHIPGROUP_celltype_3D', 'value'),
  Output('STORE_allCelltypes_3D', 'data'),
  Input('STORE_cellsObsFilter_3D', 'data'),
  Input('STORE_cellsExpFilter_3D', 'data'),
  State('DROPDOWN_stage_3D', 'value'),
  State('STORE_ctpCmap_3D', 'data'),
)
def update_chipGroupCelltype_3D(obsFilter, expFilter, stage, cmap):
  cells = list(set(obsFilter)&set(expFilter))
  cells.sort()
  
  celltypes = list(dataset[stage].obs[config['annotation']][cells].unique().astype(str))
  
  chips = [
    dmc.Chip(
      children=ctp, value=ctp, size='xs', color='gray', variant='filled', type='radio',
      styles = {
        'label': {
          'color': cmap[ctp],
          'font-size': 12,
          'font-weight': 'bold'
        },
        'checkIcon': {
          'color': cmap[ctp],
        }
      },
      id = {'type': 'CHIP_ctpColorLegend_3D', 'id': ctp}
    ) 
    for ctp in celltypes
  ]
  
  return chips, celltypes, celltypes

@callback(
  Output('CHIPGROUP_celltype_3D', 'value'),
  Input('BUTTON_invertSelectionCtp_3D', 'n_clicks'),
  State('CHIPGROUP_celltype_3D', 'value'),
  State('STORE_allCelltypes_3D', 'data'),
  prevent_initial_call=True,
)
def invertSelection_celltypesButton_3D(click, curValue, allCelltypes):
  return list(set(allCelltypes) - set(curValue))

@callback(
  Output('CHIPGROUP_celltype_3D', 'value'),
  Input('BUTTON_clearSelectionCtp_3D', 'n_clicks'),
  prevent_initial_call=True
)
def clearSelection_celltypesButton_3D(click):
  return []

@callback(
  Output('CHIPGROUP_celltype_3D', 'value'),
  Input('BUTTON_allSelectionCtp_3D', 'n_clicks'),
  State('CHIPGROUP_celltype_3D', 'value'),
  State('STORE_allCelltypes_3D', 'data'),
  prevent_initial_call=True
)
def allSelection_celltypesButton_3D(click, curValue, allCelltypes):
  if set(curValue) == set(allCelltypes):
    return no_update
  else:
    return list(set(allCelltypes))

# store_ctpInfo_forJSONtoPLot
@callback(
  Output('STORE_cellsCtpFilter_3D', 'data'),
  Input('CHIPGROUP_celltype_3D', 'value'),
  State('DROPDOWN_stage_3D', 'value')
)
def store_ctpInfo_forJSONtoPlot_3D(selectedCtps, stage):
    
  series = dataset[stage].obs[config['annotation']].astype(str)
  series = series[series.isin(selectedCtps)]
  
  return series.index.to_list()
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
# plot_3Dfigure_exp
clientside_callback(
  ClientsideFunction(
    namespace='plotFunc_3Dtab',
    function_name='exp_3Dscatter',
  ),
  Output("FIGURE_3Dexpression", "figure"),
  Input('STORE_obs_3D', 'data'),
  Input('STORE_cellsIntersection_3D', 'data'),
  Input('STORE_singleExp_3D', 'data'),
  Input('STORE_ifmulti_3D', 'data'),
  Input('STORE_mixedColor_3D', 'data'),
  State('SWITCH_hideAxes_3D', 'checked'),
  State('SWITCH_previewBox_3D', 'checked'),
  State('STORE_previewRange_3D', 'data'),
  State('SEGMENTEDCONTROL_projection_3D', 'value'),
  State('NUMBERINPUT_scatter3dPointsize_3D', 'value')
)

# colorpicker for singleExp
@callback(
  Output('ACTIONICON_colorSingle_3D', 'children'),
  Output('FIGURE_3Dexpression', 'figure'),
  Input('COLORPICKER_single_3D', 'value'),
)
def colorpicker_for_singleExp_3D(color):
  patch = Patch()
  patch['layout']['coloraxis']['colorscale'][1][1] = color
  icon = DashIconify(icon = 'fluent:circle-48-filled', color=color, width=48)
  return icon, patch

@callback(
  Output('TEXT_colorSingle_3D', 'value'),
  Output('COLORPICKER_single_3D', 'value'),
  Input('TEXT_colorSingle_3D', 'value'),
  Input('COLORPICKER_single_3D', 'value'),
  prevent_initial_call=True,
)
def linkage_colorPickerAndTextSingle_3D(value1, value2):
  id = ctx.triggered_id
  if id == 'TEXT_colorSingle_3D':
    if((len(value1)==4) or (len(value1)==7)):
      return no_update, value1
    else:
      raise PreventUpdate 
  else:
    return value2, no_update

# colopicker for multiExp

@callback(
  Output('STORE_multiNameInfo_3D', 'data'),
  Input({'type': 'COLORPICKER_multi_3D', 'index': ALL}, 'value'),
  Input({'type': 'DROPDOWN_multiName_3D', 'index': ALL}, 'value'),
)
def store_multiNameInfo_3D(colors, genes):
  return dict(zip(colors, genes))

@callback(
  Output({'type':'ACTIONICON_colorMulti_3D', 'index': MATCH}, 'children'),
  Output({'type': 'TEXT_colorMulti_3D', 'index': MATCH}, 'value'),
  Output({'type': 'COLORPICKER_multi_3D', 'index': MATCH}, 'value'),
  Input({'type': 'TEXT_colorMulti_3D', 'index': MATCH}, 'value'),
  Input({'type': 'COLORPICKER_multi_3D', 'index': MATCH}, 'value'),
  prevent_initial_call=True,
)
def linkage_colorPickerAndTextMulti_3D(value1, value2):
  id = ctx.triggered_id
  
  if id['type'] == 'TEXT_colorMulti_3D':
    if((len(value1)==4) or (len(value1)==7)):
      color = value1
      icon = DashIconify(icon = 'fluent:circle-48-filled', color=color, width=48)
      return icon, no_update, color
    else:
      raise PreventUpdate   
  else:
    color = value2
    icon = DashIconify(icon = 'fluent:circle-48-filled', color=color, width=48)
    return icon, color, no_update

# colorpicker for ctpLegend
@callback(
  Output('DRAWER_setColorCtp_3D', 'visible'),
  Input('BUTTON_setColors_3D', 'n_clicks'),
  prevent_initial_call=True,
)
def setCelltypeColorsInDrawer_3D(click):
  return True

@callback(
  Output('DRAWER_setColorCtp_3D', 'children'),
  Input('STORE_allCelltypes_3D', 'data'),
  State('STORE_ctpCmap_3D', 'data'),
  # prevent_initial_call=True, 
)
def generate_drawerLegendContent_3D(curAllCtps, cmap):
  return drawerContent_ctpColorPicker(curAllCtps, cmap)

@callback(
  Output({'type': 'ACTIONICON_colorCtp_3D', 'id': MATCH}, 'children'),
  Output({'type': 'TEXT_colorCtp_3D', 'id': MATCH}, 'value'),
  Output({'type': 'COLORPICKER_colorCtp_3D', 'id': MATCH}, 'value'),
  Input({'type': 'TEXT_colorCtp_3D', 'id': MATCH}, 'value'),
  Input({'type': 'COLORPICKER_colorCtp_3D', 'id': MATCH}, 'value'),
  prevent_initial_call=True,
)
def syncAndReturn_colorValue_3D(text, picker):


  tid = ctx.triggered_id
  celltype = tid['id']
  
  if tid['type'] == 'TEXT_colorCtp_3D':
    if((len(text)==4) or (len(text)==7)):
      color = text  
      icon = DashIconify(icon = 'fluent:circle-48-filled', color=color, width=48)
      return icon, no_update, color
    else:
      raise PreventUpdate
  else:
    color = picker
    icon = DashIconify(icon = 'fluent:circle-48-filled', color=color, width=48)
    return icon, color, no_update
  
@callback(
  Output('STORE_ctpCmap_3D', 'data'),
  Input({'type': 'TEXT_colorCtp_3D', 'id': ALL}, 'value'),
  prevent_initial_call=True
)
def update_storeCtpCmap_3D(colors):
    triggered = ctx.triggered
    triggered_id = ctx.triggered_id
    if(len(triggered) > 1):
      raise PreventUpdate
    
    color = triggered[0]['value']
    ctp = triggered_id['id']
    patch = Patch()
    patch[ctp] = color
    return patch

@callback(
  Output('FIGURE_3Dcelltype', 'figure'),
  Output('FIGURE_ctpViolin_3D', 'figure'),
  Input('STORE_ctpCmap_3D', 'data'),
  State('STORE_allCelltypes_3D', 'data'),
  prevent_initial_call=True,
)
def update_figureCtpCmap_3D(cmap, curCtps):
  
  patch_fig=Patch()
  for i in range(0, len(curCtps)):
    patch_fig['data'][i]['marker']['color'] =  cmap[curCtps[i]]
  return patch_fig, patch_fig

@callback(
  Output({'type': 'CHIP_ctpColorLegend_3D', 'id': MATCH}, 'styles'),
  Input({'type': 'TEXT_colorCtp_3D', 'id': MATCH}, 'value'),
  prevent_initial_call=True
)
def update_chipColor_3D(color):
  patch = Patch()
  patch['label']['color'] = color
  patch['checkIcon']['color'] = color
  return patch

# plot_3Dfigure_ctp
clientside_callback(
  ClientsideFunction(
    namespace='plotFunc_3Dtab',
    function_name='ctp_3Dscatter',
  ),
  Output("FIGURE_3Dcelltype", "figure"),
  Input('STORE_obs_3D', 'data'),
  Input('STORE_cellsIntersection_3D', 'data'),
  State('SWITCH_hideAxes_3D', 'checked'),
  State('SWITCH_previewBox_3D', 'checked'),
  State('STORE_previewRange_3D', 'data'),
  State('STORE_ctpCmap_3D', 'data'),
  State('SEGMENTEDCONTROL_projection_3D', 'value'),
  State('NUMBERINPUT_scatter3dPointsize_3D', 'value')
)

# sync layout between exp and ctp figure
@callback(
  Output("FIGURE_3Dexpression", "figure"),
  Output("FIGURE_3Dcelltype", "figure"),
  Input("FIGURE_3Dexpression", "relayoutData"),
  Input("FIGURE_3Dcelltype", "relayoutData"),
  State('SEGMENTEDCONTROL_projection_3D', 'value'),
  # prevent_initial_call=True,
  # background=True,
  # manager=background_callback_manager
)
def update_relayout(expLayout, ctpLayout, proj):
  tid = ctx.triggered_id
  patch = Patch()
  
  if tid == 'FIGURE_3Dexpression':
    
    if 'scene.camera' in expLayout:
      patch['layout']['scene']['camera'] = expLayout['scene.camera']
    if 'scene.aspectratio' in expLayout:
      patch['layout']['scene']['aspectmode'] = 'manual'
      patch['layout']['scene']['aspectratio'] = expLayout['scene.aspectratio']

    return patch, patch

  elif tid == 'FIGURE_3Dcelltype':
    
    if 'scene.camera' in ctpLayout:
      patch['layout']['scene']['camera'] = ctpLayout['scene.camera']
    if 'scene.aspectratio' in ctpLayout:
      patch['layout']['scene']['aspectmode'] = 'manual'
      patch['layout']['scene']['aspectratio'] = ctpLayout['scene.aspectratio']

    return patch, patch
  
  else:
    raise PreventUpdate

# update scatter-3d point size
@callback(
  Output('FIGURE_3Dexpression', 'figure'),
  Input('NUMBERINPUT_scatter3dPointsize_3D', 'value'),
  prevent_initial_call = True
)
def update_expPointSize_3D(size):
  
  patch = Patch()
  patch['data'][0]['marker']['size'] = size
  
  return patch

@callback(
  Output('FIGURE_3Dcelltype', 'figure'),
  Input('NUMBERINPUT_scatter3dPointsize_3D', 'value'),
  State('STORE_cellsIntersection_3D', 'data'),
  State('DROPDOWN_stage_3D', 'value'),
  prevent_initial_call = True,
)
def update_ctpPointSize_3D(size, cells, stage):
  
  celltypes = dataset[stage].obs.loc[cells, config['annotation']].unique().astype(str)
  patch = Patch()
  for i in range(0,len(celltypes)):
    patch['data'][i]['marker']['size'] = size
  return patch

# switch projection type
@callback(
  Output('FIGURE_3Dcelltype', 'figure'),
  Output('FIGURE_3Dexpression', 'figure'),
  Input('SEGMENTEDCONTROL_projection_3D', 'value'),
)
def switch_projectionType(type):
  patch=Patch()
  patch['layout']['scene']['camera']['projection'] = {'type': type}
  return patch, patch

# find intersection of 3-filter
@callback(
  Output('STORE_cellsIntersection_3D', 'data'),
  Input('STORE_cellsObsFilter_3D', 'data'),
  Input('STORE_cellsExpFilter_3D', 'data'),
  Input('STORE_cellsCtpFilter_3D', 'data'),
)
def intersection_of_filter(obsFilter, expFilter, ctpFilter):
  tmp = list(set(obsFilter) & set(expFilter) & set(ctpFilter))
  tmp.sort()
  return tmp

# hide axes
@callback(
  Output("FIGURE_3Dexpression", "figure", allow_duplicate=True),
  Output("FIGURE_3Dcelltype", "figure", allow_duplicate=True),
  Input('SWITCH_hideAxes_3D', 'checked'),
  prevent_initial_call=True
)
def hideAxes_3D(hideAxes):
  patch = Patch()
  if hideAxes:
    patch['layout']['scene']['xaxis']['visible'] = False
    patch['layout']['scene']['yaxis']['visible'] = False
    patch['layout']['scene']['zaxis']['visible'] = False
  else: 
    patch['layout']['scene']['xaxis']['visible'] = True
    patch['layout']['scene']['yaxis']['visible'] = True
    patch['layout']['scene']['zaxis']['visible'] = True
  return patch, patch

# show preview Box
@callback(
  Output('FIGURE_3Dexpression', 'figure', allow_duplicate=True),
  Output('FIGURE_3Dcelltype', 'figure', allow_duplicate=True),
  Input('SWITCH_previewBox_3D', 'checked'),
  Input('STORE_previewRange_3D', 'data'),
  prevent_initial_call=True,
)
def update_previewBox(showBox, preRange):
  patch = Patch()
  if showBox:
    patch['data'][-1] = {
                    'x': [preRange['x_min'], preRange['x_min'], preRange['x_min'], preRange['x_min'],
                          preRange['x_max'], preRange['x_max'], preRange['x_max'], preRange['x_max']],
                    'y': [preRange['y_min'], preRange['y_max'], preRange['y_min'], preRange['y_max'],
                          preRange['y_min'], preRange['y_max'], preRange['y_min'], preRange['y_max']],
                    'z': [preRange['z_min'], preRange['z_min'], preRange['z_max'], preRange['z_max'],
                          preRange['z_min'], preRange['z_min'], preRange['z_max'], preRange['z_max']],
                    'i': [0, 1, 0, 0, 0, 0, 2, 2, 7, 7, 7, 7],
                    'j': [1, 2, 4, 1, 4, 2, 3, 6, 4, 4, 1, 1],
                    'k': [2, 3, 5, 5, 6, 6, 7, 7, 6, 5, 3, 5],
                    'color': 'black', 'opacity': 0.60, 'type': 'mesh3d'
                  }
  else:
    patch['data'][-1] = {
                    'x': [], 'y': [], 'z': [], 'i': [], 'j': [], 'k': [],
                    'type': 'mesh3d', 'color': 'black', 'opacity': 0.60
                  }

  return patch, patch

# violin plot
@callback(
  Output('FIGURE_expViolin_3D', 'figure'),
  Input('DROPDOWN_featureType_3D', 'value'),
  Input('DROPDOWN_stage_3D', 'value'),
  Input('STORE_cellsIntersection_3D', 'data'),
  Input('STORE_ifmulti_3D', 'data'),
  Input('BUTTON_singlePlot_3D', 'n_clicks'),
  Input('BUTTON_multiPlot_3D', 'n_clicks'),
  State('DROPDOWN_singleName_3D', 'value'),
  State('STORE_multiNameInfo_3D', 'data'),
  State('SEGMENTEDCONTROL_violinPoints_3D', 'value'),
  State('NUMBERINPUT_violinPointpos_3D', 'value'),
  State('NUMBERINPUT_violinPointsize_3D', 'value'),
  State('NUMBERINPUT_violinPointjitter_3D', 'value'),
  State('SEGMENTEDCONTROL_violinBox_3D', 'value'),
  State('NUMBERINPUT_violinBoxwidth_3D', 'value'),
  # background = True,
  # manager = background_callback_manager,
)
def update_spatial_plotFeature3D_expViolin(featureType, stage, cells, ifmulti, splot, mplot, sname, minfo, 
                                           points, pointpos, pointsize,jitter, box, boxwidth):
  
  points = False if points=='none' else points
  
  box_visible = True if box=='box' or box=='all' else False
  meanline_visible = True if box=='meanline' or box=='all' else False

  if not ifmulti:
    fig = show_expViolin(dataset[stage][cells], sname, points=points, pointpos=pointpos, marker_size=pointsize, 
                         meanline_visible=meanline_visible,  box_visible=box_visible, jitter=jitter, box_width=boxwidth)
  else:
    fig = show_multiFeatures_expViolin(dataset[stage][cells], minfo, points=points, pointpos=pointpos, marker_size=pointsize, 
                                       meanline_visible=meanline_visible,  box_visible=box_visible, jitter=jitter, box_width=boxwidth)

  return fig

@callback(
  Output('FIGURE_ctpViolin_3D', 'figure'),
  Input('DROPDOWN_featureType_3D', 'value'),
  Input('DROPDOWN_stage_3D', 'value'),
  Input('STORE_cellsIntersection_3D', 'data'),
  Input('STORE_ifmulti_3D', 'data'),
  Input('BUTTON_singlePlot_3D', 'n_clicks'),
  Input('BUTTON_multiPlot_3D', 'n_clicks'),
  State('DROPDOWN_singleName_3D', 'value'),
  State('STORE_multiNameInfo_3D', 'data'),
  State('SEGMENTEDCONTROL_violinPoints_3D', 'value'),
  State('NUMBERINPUT_violinPointpos_3D', 'value'),
  State('NUMBERINPUT_violinPointsize_3D', 'value'),
  State('NUMBERINPUT_violinPointjitter_3D', 'value'),
  State('SEGMENTEDCONTROL_violinBox_3D', 'value'),
  State('NUMBERINPUT_violinBoxwidth_3D', 'value'),
  # background = True,
  # manager = background_callback_manager,
)
def update_spatial_plotFeature3D_ctpExpViolin(featureType, stage, cells, ifmulti, splot, mplot, sname, minfo, 
                                              points, pointpos, pointsize, jitter, box, boxwidth):

  points = False if points=='none' else points
  
  box_visible = True if box=='box' or box=='all' else False
  meanline_visible = True if box=='meanline' or box=='all' else False

  if not ifmulti:
    fig = show_ctpExpViolin(dataset[stage][cells], sname, points=points, pointpos=pointpos, marker_size=pointsize, 
                            meanline_visible=meanline_visible, box_visible=box_visible, jitter=jitter, box_width=boxwidth)
  else:
    fig = show_multiFeatures_ctpExpViolin(dataset[stage][cells], minfo, points=points, pointpos=pointpos, marker_size=pointsize, 
                                          meanline_visible=meanline_visible, box_visible=box_visible, jitter=jitter, box_width=boxwidth)

  return fig

# moran SVG offcanvas
@callback(
  Output('OFFCANVAS_moranRes_3D', 'is_open'),
  Input('BUTTON_showMoran_3D', 'n_clicks'),
  prevent_initial_call = True
)
def show_moranRes_offcanvas(click):
  if click:
    return True

@callback(
  Output('DATATABLE_moranRes_3D', 'data'),
  Output('DATATABLE_moranRes_3D', 'columns'),
  
  Input('BUTTON_calMoran_3D', 'n_clicks'),
  State('STORE_cellsIntersection_3D', 'data'),
  State('DROPDOWN_stage_3D', 'value'),
  State('DROPDOWN_featureType_3D', 'value'),
  prevent_initial_call=True,
  background = True,
  # manager = background_callback_manager,
  running = [
    (Output('BUTTON_showMoran_3D', 'disabled'), True, False),
    (Output('BUTTON_calMoran_3D', 'children'), '< 1min', 'Compute'),
    (Output('BUTTON_calMoran_3D', 'loading'), True, False),
    (Output('OFFCANVAS_moranRes_3D', 'is_open'), False, True),
  ]
)
def cal_moranRes(click, cells, stage, featureType):
  
  
  df = cal_moran_3D(dataset[stage][cells])
  df = df.reset_index(names='Feature')
  return (df.to_dict('records'),
          [
            {"name": i, "id": i, "deletable": False, 'type': 'numeric', 
              'format':Format(precision=4)} 
            for i in df.columns
          ]
        )

# camera angle adjust
@callback(
  Output('PRE_camera_angle_3D', 'children'),
  Input('BUTTON_get_angle_3D', 'n_clicks'),
  State('FIGURE_3Dcelltype', 'figure'),
)
def get_camera_angle_and_display(click, figure):
  if click:
    angle_json = figure['layout']['scene']['camera']
    return json.dumps(
        angle_json,
        indent=2,
        ensure_ascii=False,
    )
  raise PreventUpdate

@callback(
  Output('FIGURE_3Dcelltype', 'figure'),
  Output('FIGURE_3Dexpression', 'figure'),
  Input('BUTTON_set_angle_3D', 'n_clicks'),
  State('PRE_camera_angle_3D', 'children'),
)
def set_camera_angle(click, angle_json):
  if click:
    patch = Patch()
    patch['layout']['scene']['camera'] = json.loads(angle_json.strip())
    return patch, patch
  raise PreventUpdate
# In[] app/run:

tabs = dbc.Col(
  spatial_tabs,
  id = 'tabs'
)

dcc.Graph

layout = dbc.Container(
    [
      dmc.NotificationsProvider(),
      html.Div(id='notifications-container-spatial'),
      dbc.Row([
        dbc.Col([
          tabs,
        ], width=12)
      ],)
    ],
  fluid=True,
  className="Container-all",
)

