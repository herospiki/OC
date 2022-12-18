import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def plot_waterfall(best_features, shap_values, prediction):
    measures = ['relative']*20
    if (prediction == 1):
        fig = go.Figure(go.Waterfall(
            name="Prêt refusé", orientation="h", measure=measures, y=best_features,
            x=shap_values,
            decreasing={"marker": {"color": "Green"}},
            increasing={"marker": {"color": "Red"}},
            connector={"mode": "between", "line": {"width": 4, "color": "rgb(0, 0, 0)", "dash": "solid"}}))
        fig.update_layout(title="Prêt refusé",  height=600,
                          yaxis={'side': 'right'})
        fig.update_yaxes(tickangle=-45)

        return fig
    else:
        fig = go.Figure(go.Waterfall(name="Prêt accordé", orientation="h", measure=measures, y=best_features, x=shap_values,
                                     decreasing={"marker": {"color": "Green"}},
                                     increasing={"marker": {"color": "Red"}},
                                     connector={"mode": "between", "line": {"width": 4, "color": "rgb(0, 0, 0)", "dash": "solid"}}))
        fig.update_layout(title="Prêt accordé", height=600,
                          yaxis={'side': 'right'})
        fig.update_yaxes(tickangle=-45)
        return fig


def format_values(df):
    df = df.replace('(-0.001, 0.1]', 0)
    df = df.replace('(0.9, 1.0]', 1)
    df['target'] = df['target'].replace(0, 'Fiable')
    df['target'] = df['target'].replace(1, 'Défaut de paiement')
    return df


def get_value(interval):
    if interval == '(-0.001, 0.1]':
        return 0
    else:
        if interval == '(0.9, 1.0]':
            return 1
        else:
            return interval


def plot_comparison(value, interval, target, bins, percent_of_target):
    df = pd.DataFrame()
    df['target'] = target
    df['target'] = df['target'].astype('category')
    df['bins'] = bins
    df['percent_of_target'] = percent_of_target
    df2 = format_values(df)
    text_val = str(value)
    fig = px.bar(df2, x='bins', y='percent_of_target', color='target', barmode='group',
                 color_discrete_map={'Fiable': 'green', 'Défaut de paiement': ' red'})
    fig.add_vline(x=str(get_value(interval)))
    fig.update_xaxes(title='Intervalles/valeurs')
    fig.update_yaxes(title='%')
    fig.update_layout(title = 'client : ' + text_val, width=600)
    return fig
