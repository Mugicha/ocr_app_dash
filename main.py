import cv2
import base64
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output

app = dash.Dash()

def update_camera_image(n_clicks):
    """
    カメラから画像を取得するための処理.

    :param n_clicks:
    :return:
    """

    # 取得.
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()

    # 画像をエンコード
    _, buffer = cv2.imencode('.png', frame)
    b64_bytes = base64.b64encode(buffer)
    b64_string = b64_bytes.decode()

    return 'data:image/png;base64,{}'.format(b64_string)

app.layout = html.Div([
    dcc.Graph(id='image',

              # 取得した画像にバウンディングボックスを
              # 描画するための処理①
              # https://plotly.com/python/imshow/
              config={'modeBarButtonsToAdd':['drawline',
                                             'drawopenpath',
                                             'drawclosedpath',
                                             'drawcircle',
                                             'drawrect',
                                             'eraseshape',
                                             ]
                      }
              ),
    html.Button('Update image', id='button'),
])

@app.callback(Output('image', 'figure'), [Input('button', 'n_clicks')])
def update_image(n_clicks):

    # 画像を表示するためのFigureを作成
    figure = go.Figure()

    # カメラから画像を取得.
    img = go.Image(source=update_camera_image(n_clicks))

    # グラフや画像をFigureに追加.
    figure.add_trace(img)

    # 取得した画像にバウンディングボックスを
    # 描画するための処理②
    figure.update_layout(dragmode='drawrect',
                         newshape=dict(line_color='cyan'),
                         )

    return figure

if __name__ == '__main__':
    app.run_server(host='0.0.0.0')
