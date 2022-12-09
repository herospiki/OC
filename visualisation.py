import plotly 
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
        fig.update_layout(title="Prêt refusé", width=800, height=600)
        return fig
    else:
        fig = go.Figure(go.Waterfall(name="Prêt accordé", orientation="h", measure=measures, y=best_features, x=shap_values,
                                     decreasing={"marker": {"color": "Green"}},
                                     increasing={"marker": {"color": "Red"}},
                                     connector={"mode": "between", "line": {"width": 4, "color": "rgb(0, 0, 0)", "dash": "solid"}}))
        fig.update_layout(title="Prêt accordé", width=800, height=600)
        return fig



def plot_comparison(interval, target, bins, percent_of_target):
    df = pd.DataFrame()
    df['target'] = target
    df['target'] = df['target'].astype('category')
    df['bins'] = bins
    df['percent_of_target'] = percent_of_target
    #df['bin_str'] = df['bin'].astype(str) #pour affichage
    #df['TARGET'] = df['TARGET'].astype('category')
    fig = px.bar(df, x= 'bins', y = 'percent_of_target', color='target', barmode='group', 
    color_discrete_map={0: 'green', 1:' red'})
    fig.add_vline(x = str(interval)) # color correspondant au target + annotation
    fig.update_xaxes(title='Intervalles')
    fig.update_yaxes(title='%')
    fig.update_layout(width=600)
    return fig



def comparison_figure(df, best_features, client_id):
    df['client'] = 1
    df.iat[client_id,len(df.columns)+1] = 3 # Focus sur le client
    
    df_melted = pd.melt(df,  id_vars=['TARGET','client'], value_vars=best_features).rename(columns={
        "variable": "features",
        "value": "shap_value"
})
    df_melted['client'] = df_melted['client'].astype('category')

    fig = px.scatter(df_melted,     
                    x="shap_value",
                    y="features",  
                    color='client', 
                #color_discrete_map={"setosa": "rgb(0,0,255)", "versicolor": "rgb(255,0,0)", "virginica": "rgb(0,255,0)"},
                    symbol='client',
                #symbol_map={'3': "x_thin", '1' : "circle"}
                )
    fig.update_layout(
        title="Positionnement du client",
        font_size=11,
        height=600,
        width=600, showlegend= False)
    return fig

