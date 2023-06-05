
from dash import Dash, html, dcc
from datetime import date
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from dash.exceptions import PreventUpdate
import base64

# имя картинки в качестве баннера, его ширина и высота
FILENAME_BANNER_IMAGE = "/home/yu/Рабочий стол/artem_veselov/dash_meter/assets/i1.jpg"
WIDTH_IMAGE = 100
HEIGHT_IMAGE = 100

class View():
    def __init__(self, db):
        self.app = Dash(__name__)
        self.date_start = [2017,12,25]
        self.date_end = [2025,12,25]
        self.db = db
        self.max_count_values = 30
        
        # Внутренний кэш вьюшки
        self.cache_names = []
        self.cache_values = []
        self.cache_dates = []

        # фигуры для графов
        self.figure_last = go.Figure(data=[go.Scatter()])
        self.figure_history = go.Figure(data=[go.Scatter()])
        
        self.set_ui()
        self.set_callback()

    # установка интерфейса
    def set_ui(self):
        self.figure_last = self.set_last_values()
        encoded_image = base64.b64encode(open(FILENAME_BANNER_IMAGE, 'rb').read())
        self.app.layout = html.Div([
                html.Img(width=WIDTH_IMAGE, height=HEIGHT_IMAGE ,src='data:image/png;base64,{}'.format(encoded_image.decode())),
                html.H1("График последних 30-ти значений"),
                dcc.Graph(id="graph-last", figure=self.figure_last),
                html.Div(id="label-info-last"),
                dcc.Interval(
                    id='interval-graph-last',
                    interval=1*1000,
                    n_intervals=0
                ),
                html.Hr(),

                html.H1("История значений"),
                dcc.DatePickerSingle(
                    id='date-picker-start',
                    clearable=True,
                    with_portal=True,
                    date=date(self.date_start[0],
                            self.date_start[1],
                            self.date_start[2]),
                    calendar_orientation='vertical',
                    placeholder='Select a date start',
                ),
                dcc.DatePickerSingle(
                    id='date-picker-end',
                    clearable=True,
                    with_portal=True,
                    date=date(self.date_end[0],
                            self.date_end[1],
                            self.date_end[2]),
                    calendar_orientation='vertical',
                    placeholder='Select a date end',
                ),
                html.Div(id="label-info-history"),
                dcc.Graph(id="graph-history", figure=self.figure_history),
        ])
        return self.app.layout


    # установка функций обратного вызова
    # для обработки поьзовательских действий
    # (настройка диапозона даты)
    # (наведение курсора на график)
    def set_callback(self):
        # установка колбэка для выбора даты
        @self.app.callback(Output('graph-history', 'figure'),
                        [Input('date-picker-start', 'date'),
                        Input('date-picker-end', 'date')])
        def update_history_graph(date1, date2):
            if (date1 is None) or (date2 is None):
                raise PreventUpdate
            else:
                self.date_start, self.date_end = self.db.read_slice_time(date1, date2)
                self.cache_names = self.db.select_names
                self.cache_values = self.db.select_values
                self.cache_dates = self.db.select_dates
                coord_x = [x for x in range(len(self.cache_names)-1)]
                coord_y = self.cache_values
                self.figure_history = go.Figure(
                            data=[go.Scatter(
                                x=coord_x, 
                                y=coord_y,
                            )])
                self.figure_history.update_traces(marker_size=20)
            return self.figure_history
                
        # установка колбэка для автот обновления 
        # графика на 30 последних значений
        @self.app.callback(Output('graph-last', 'figure'),
              Input('interval-graph-last', 'n_intervals'))
        def update_graph_last(n):
            self.figure_last = self.set_last_values()
            self.figure_last.update_traces(marker_size=20)
            return self.figure_last

        # установка колбэка при наведениии на график истории
        @self.app.callback(Output('label-info-history', 'children'),
                Input('graph-history', 'hoverData'))
        def update_info_history(point):
            if (point is None):
                raise PreventUpdate
            else:
                x, y = self.get_point(point)
            return f"Value: {y}, Date: {self.cache_dates[x]}, Image: {self.cache_names[x]}"
        
        # установка колбэка при наведениии на график последних 30-ти значений                
        @self.app.callback(Output('label-info-last', 'children'),
              Input('graph-last', 'hoverData'))
        def update_info_last(point):
            if (point is None):
                raise PreventUpdate
            else:
                x, y = self.get_point(point)
            return f"Value: {y}, Date: {self.cache_dates[x]}"


    def get_point(self, p):
        x = p['points'][0]['x']
        y = p['points'][0]['y']
        return x, y
            
    # загрузка выборки данных из таблицы (количество - константа: self.max_count_values) 
    def set_last_values(self):
        names, values, dates = self.db.read_all_rows()
        count_values_now = 0
        if len(values)-1 <= self.max_count_values:
            count_values_now = len(values)
        else:
            count_values_now = self.max_count_values

        coord_x = [x for x in range(count_values_now)]
        start_ind = -(count_values_now)-1
        coord_y = values[start_ind:]
        self.figure_last = go.Figure(
                    data=[go.Scatter(
                        x=coord_x, 
                        y=coord_y,
                    )])
        return self.figure_last  
    
    # Установить True/False для режима отладки-дебага
    def launch(self):
        self.app.run_server(debug=False)





    

    
