import plotly.graph_objects as go
import numpy as np
import pandas as pd

class Graphs:

    def __init__(self, symbol=None):
        self._symbol = symbol
        self._missing_dates = {}

    def update_symbol(self, symbol):
        self._symbol = symbol

        return None

    def _filter_missing_dates(self, data, timeframe):

        if timeframe not in self._missing_dates:

            # build complete timeline from start date to end date
            all_dates = pd.date_range(start=data['time'].iat[0],end=data['time'].iat[-1])

            # retrieve the dates that ARE in the original datset
            original_dates = [d.strftime("%Y-%m-%d") for d in data['time']]

            # define dates with missing values
            break_dates = [d for d in all_dates.strftime("%Y-%m-%d").tolist() if not d in original_dates]

            self._missing_dates[timeframe] = break_dates

        return self._missing_dates[timeframe]

    def _filter_data(self, data, start_time):
        return data[data['time'] >= start_time]

    def _add_sma_graphs(self, fig, data, color, col_name):
        
        fig.add_trace(
            go.Scatter(
                x=data['time'], 
                y=data[col_name],
                line=dict(color=color, width=1),
                name=col_name.upper()
            )
        )

        return None

    def _draw_hline(self, fig, y_val, line_dash, line_col, annotation=None):

        fig.add_hline(
            y=y_val,
            line_dash=line_dash,
            line_color=line_col,
            annotation_text=annotation or '',
            line_width=3
        )
        
        return None

    def _fill_missing_dates(self, fig, data_day, timeframe):
        fig.update_xaxes(
            rangebreaks=[
                dict(
                    values=self._filter_missing_dates(data_day, timeframe)
                )
            ]
        )

        return None

    def plot_atr(self, data):
        
        atr_fig = go.Figure([
            go.Scatter(
                x=data['time'], 
                y=data['atr'],
                mode="lines"
            )
        ])

        current_atr = str(data['atr'].iat[-1]).split('.')
        current_atr = [num for num in current_atr[1] if num != '0']
        current_atr = ''.join(current_atr[:2])

        atr_fig.update_layout(
            title=f"{self._symbol} - ATR (4H) (Current value: {current_atr})",
            template='simple_white',
            xaxis_title="Time",
            hovermode='x',
            xaxis_rangeslider_visible=False,
            showlegend=False,
            yaxis={'visible': False, 'showticklabels': False}
        )

        return atr_fig

    def plot_candlesticks_fullday(self, data_day, timeframe, indicators_df):

        candlesticks_minute_fig = go.Figure(
            data=[
                go.Candlestick(
                    x=data_day['time'],
                    open=data_day['open'], 
                    high=data_day['high'],
                    low=data_day['low'], 
                    close=data_day['close'],
                    hoverinfo='none',
                    showlegend=False
                )
            ]
        )

        self._add_sma_graphs(candlesticks_minute_fig, indicators_df, 'black', 'sma_50')

        if timeframe == '15M':
            self._add_sma_graphs(candlesticks_minute_fig, indicators_df, 'blue','sma_21')
            self._add_sma_graphs(candlesticks_minute_fig, indicators_df, 'red','sma_200')

        legend_config=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )

        candlesticks_minute_fig.update_layout(
            title=f"{self._symbol} - Series ({timeframe})",
            xaxis_title="Time",
            yaxis_title="Price",
            hovermode='x',
            yaxis_tickformat='.5f',
            xaxis_rangeslider_visible=False,
            legend=legend_config
        )

        self._fill_missing_dates(candlesticks_minute_fig, data_day, timeframe)
        
        return candlesticks_minute_fig

    def plot_rsi_figure(self, rsi_today, start_time):

        rsi_fig = go.Figure([
            go.Scatter(
                x=rsi_today['time'], 
                y=rsi_today['value'],
                mode="lines"
            )
        ])

        rsi_fig.update_layout(
            xaxis_title="Time",
            yaxis_title="RSI Value",
            title=f"RSI of {self._symbol}",
            hovermode='x',
            yaxis_tickformat='.2f'
        )

        self._draw_hline(rsi_fig, 50, "solid", "black")

        self._fill_missing_dates(rsi_fig, rsi_today, '1H')

        return rsi_fig

    def plot_pip_target(self, data):
        
        x_axis_val = list(data.keys())

        profit_targets = [target['profit'] for target in data.values()]
        loss_targets = [target['loss'] for target in data.values()]

        bar_fig = go.Figure(
            [
                go.Bar(
                    x=x_axis_val, 
                    y=profit_targets,
                    marker_color='green',
                    name='Profit',
                    opacity=0.5
                ),
                go.Bar(
                    x=x_axis_val,
                    y=loss_targets,
                    marker_color='indianred',
                    name='Loss',
                    opacity=0.5
                )
            ]
        )

        bar_fig.update_layout(
            template='simple_white',
            xaxis_title="symbol",
            yaxis_title="Points",
            title=f"Average points target",
            hovermode='x unified',
            height=700
        )

        return bar_fig

    def display_symbol_strength(self, data):

        roc_values = list(data.values())
        marker_colors = ['green' if roc > 0 else 'red' for roc in roc_values]

        bar_fig = go.Figure(
            [
                go.Bar(
                    x=list(data.keys()), 
                    y=roc_values,
                    marker_color=marker_colors,
                    name='ROC',
                    opacity=0.35
                )
            ]
        )

        self._draw_hline(bar_fig, 0, "solid", "black")

        bar_fig.update_layout(
            template='simple_white',
            xaxis_title="symbol",
            yaxis_title="Strength",
            title=f"symbol Strength (with JPY as the apple)",
            hovermode='x unified',
            height=700
        )

        return bar_fig

    def plot_point_percentage_target(self, data_dict):

        x_val = list(data_dict.keys())
        y_val = list(data_dict.values())

        fig = go.Figure(
            [
                go.Scatter(
                    x=x_val, 
                    y=y_val,
                    mode="lines"
                )
            ]
        )

        fig.update_layout(
            title=f"Points percentage target",
            xaxis_title="Percentage",
            yaxis_title="Points",
            hovermode='x',
            xaxis=dict(
                tickmode='linear',
                tick0 = 0,
                dtick = 10
            )
        )

        return fig
    
    def plot_profit_percentage_target(self, data_dict):

        x_val = list(data_dict.keys())
        y_val = list(data_dict.values())

        fig = go.Figure(
            [
                go.Scatter(
                    x=x_val, 
                    y=y_val,
                    mode="lines"
                )
            ]
        )

        fig.update_layout(
            title=f"Profit percentage target",
            xaxis_title="Percentage",
            yaxis_title="Profit",
            hovermode='x',
            xaxis=dict(
                tickmode='linear',
                tick0 = 0,
                dtick = 10
            )
        )

        return fig