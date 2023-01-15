import cv2
import base64
import dash
import time
import pandas as pd
import plotly.graph_objs as go
from dash import dash_table
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

app = dash.Dash()
df = pd.DataFrame(data={"x0": [], "y0": [], "x1": [], "y1": []})


# カメラオブジェクト
cap = cv2.VideoCapture(2)
time.sleep(5)


def update_camera_image(n_clicks):
    """
    カメラから画像を取得するための処理.

    :param n_clicks:
    :return:
    """
    ret, frame = cap.read()

    # 画像をエンコード
    _, buffer = cv2.imencode('.png', frame)
    b64_bytes = base64.b64encode(buffer)
    b64_string = b64_bytes.decode()

    return 'data:image/png;base64,{}'.format(b64_string)


def update_annotated_table(_graph_relayoutData):
    _x0 = []
    _y0 = []
    _x1 = []
    _y1 = []
    for i in range(len(_graph_relayoutData['shapes'])):
        each_element = _graph_relayoutData['shapes'][i]
        _x0.append(int(each_element["x0"]))
        _y0.append(int(each_element["y0"]))
        _x1.append(int(each_element["x1"]))
        _y1.append(int(each_element["y1"]))
    return pd.DataFrame(data={"x0": _x0, "y0": _y0, "x1": _x1, "y1": _y1})


app.layout = html.Div([

    # カメラから取得した画像を描画する画面.
    dcc.Graph(id='live-update-graph',

              # 取得した画像にバウンディングボックスを
              # 描画するための処理①
              # https://plotly.com/python/imshow/
              config={'modeBarButtonsToAdd':['drawrect',
                                             'eraseshape',
                                             ]
                      }
              ),

    # 更新のインターバルを設定
    # 使用した端末だと0.5secが限界っぽい.
    dcc.Interval(
        id='interval-component',
        interval=1.0*1000, # in milliseconds
        n_intervals=0,
    ),

    # 画像を取得するボタン.
    html.Button('Capture.', id='capture_button'),
    html.Button('RE Capture.', id='re_capture_button'),
    html.Div(children="coordinate: None", id='coordinate_div'),
    dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns], id='annotated_table')
])


@app.callback(Output('live-update-graph', 'figure'), [Input('interval-component', 'n_intervals')])
def update_graph(n):

    # 画像を表示するためのFigureを作成
    figure = go.Figure()

    # カメラから画像を取得.
    img = go.Image(source=update_camera_image(n))

    # 画像をFigureに追加.
    figure.add_trace(img)

    # 取得した画像にバウンディングボックスを
    # 描画するための処理②
    figure.update_layout(dragmode='drawrect',
                         newshape=dict(fillcolor='turquoise', opacity=0.5),
                         )

    return figure


@app.callback(Output('interval-component', 'disabled'), [Input('capture_button', 'n_clicks')])
def disable_interval(n_clicks):

    # 起動時に何故かこの関数が呼び出されるので、
    # 処理を実行しないようにする.
    ctx = dash.callback_context
    if not ctx.triggered or ctx.triggered[0]['value'] is None:
        return dash.no_update

    # ボタンをクリックして呼び出されたときは、
    # カメラとインターバルを止める.
    cap.release()
    return True


@app.callback(Output('annotated_table', 'data'),
              [Input('live-update-graph', 'relayoutData')])
def update_table(graph_relayoutData):
    """
    callbackによるDataTableの更新.
    このあたりが参考になった.
    https://dash.plotly.com/datatable
    https://stackoverflow.com/questions/59229291/updating-dash-datatable-using-callback-function

    :param graph_relayoutData:
    :return:
    """

    if graph_relayoutData is None or "shapes" not in graph_relayoutData.keys():
        return dash.no_update

    _df = update_annotated_table(graph_relayoutData)
    return _df.to_dict('records')


if __name__ == '__main__':
    app.run_server(host='0.0.0.0')
