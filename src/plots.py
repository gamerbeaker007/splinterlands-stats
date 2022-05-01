import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.static_values_enum import Leagues

IMAGES_HEIGHT = 720
IMAGES_WIDTH = 1280

TEXT_FONT = dict(
    family="sans serif",
    size=14,
    color="floralwhite"
)

PAPER_BGCOLOR = 'rgba(100,100,100,255)'
PLOT_BGCOLOR = 'rgba(0,0,0,0)'
GRID_COLOR = 'rgba(255,255,255,255)'


def plot_season_stats_rating(season_df):

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    trace1 = go.Scatter(x=season_df.season_id,
                        y=season_df.rating,
                        mode='lines+markers',
                        name='end rating',
                        line=dict(color='firebrick', width=2),
                        )
    trace2 = go.Bar(x=season_df.season_id,
                    y=season_df.rating,
                    showlegend=False,
                    name='not displayed ony to create secondary axis',
                    opacity=0,
                    )

    trace3 = go.Bar(x=season_df.season_id,
                    y=season_df.end_league_rating,
                    name='end league',
                    offset=-0.3,
                    width=0.6,
                    marker=dict(
                        color='rgb(8,48,107)',
                        line_color='rgb(8,48,107)',
                        line_width=1),
                    opacity=1,
                    )

    fig.add_trace(trace1, secondary_y=True)
    fig.add_trace(trace2)
    fig.add_trace(trace3)

    fig.update_layout(
        paper_bgcolor=PAPER_BGCOLOR,
        plot_bgcolor=PLOT_BGCOLOR,
        font=TEXT_FONT,

        xaxis=dict(
            tickvals=season_df.season_id,
        ),

        yaxis2=dict(
            showgrid=True,
            title="rating",
            gridcolor="gray",
            gridwidth=1,
            nticks=50,
            range=[0, season_df.rating.max()*1.05]
        ),
        yaxis=dict(
            showgrid=False,
            title="league",
            range=[0, season_df.rating.max()*1.05],
            tickvals=[0, 400, 700, 1000, 1300, 1600, 1900, 2200, 2500, 2800, 3100, 3400, 3700, 4200, 4700, 9999],
            ticktext=[Leagues(0).name,
                      Leagues(1).name,
                      Leagues(2).name,
                      Leagues(3).name,
                      Leagues(4).name,
                      Leagues(5).name,
                      Leagues(6).name,
                      Leagues(7).name,
                      Leagues(8).name,
                      Leagues(9).name,
                      Leagues(10).name,
                      Leagues(11).name,
                      Leagues(12).name,
                      Leagues(13).name,
                      Leagues(14).name,
                      Leagues(15).name],
        ),
    )

    # fig.show()
    fig.write_image("output\\1_season_stats_rating.png", width=IMAGES_WIDTH, height=IMAGES_HEIGHT)


def plot_season_stats_battles(season_df):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    trace3 = go.Scatter(x=season_df.season_id, y=season_df.win_pct, mode='lines+markers', name='win percentage')
    trace4 = go.Scatter(x=season_df.season_id, y=season_df.battles, mode='lines', name='battles')
    trace5 = go.Scatter(x=season_df.season_id, y=season_df.wins, mode='lines', name='wins')
    fig.add_trace(trace3, secondary_y=True)
    fig.add_trace(trace4)
    fig.add_trace(trace5)
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor=GRID_COLOR)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor=GRID_COLOR)

    fig.update_layout(
        paper_bgcolor=PAPER_BGCOLOR,
        plot_bgcolor=PLOT_BGCOLOR,
        font=TEXT_FONT,

        xaxis=dict(
            tickvals=season_df.season_id,
        ),
        yaxis1=dict(
            showgrid=False,
            title="battles",
        ),
        yaxis2=dict(
            showgrid=False,
            overlaying='y2',
            side='right',
            anchor='x2',
            range=[0, 100],
            title='win (%)'),
    )
    # fig.show()
    fig.write_image("output\\2_season_stats_battles.png", width=IMAGES_WIDTH, height=IMAGES_HEIGHT)


def plot_season_stats_earnings(season_df):
    fig = go.Figure()
    credits_earned = season_df.credits_quest_rewards + season_df.credits_season_rewards
    sps_earned = season_df.sps_claim_staking_rewards + season_df.sps_token_award
    dec_earned = season_df.dec_reward + season_df.dec_quest_rewards + season_df.dec_season_rewards
    dec_rental_earned = season_df.dec_rental_payment + season_df.dec_rental_payment_fees
    dec_rental_payed = season_df.dec_market_rental + season_df.dec_rental_refund
    dec_tournament = season_df.dec_tournament_prize + season_df.dec_enter_tournament
    dec_total = dec_earned + dec_rental_earned + dec_rental_payed + dec_tournament
    trace1 = go.Scatter(x=season_df.season_id, y=credits_earned, mode='lines+markers',  name='credits (quest + season reward)')
    trace2 = go.Scatter(x=season_df.season_id, y=sps_earned, mode='lines+markers',  name='sps (staking + token award)')
    trace3 = go.Scatter(x=season_df.season_id, y=dec_earned, mode='lines+markers',  name='dec (ranked + quest + season)')
    trace4 = go.Scatter(x=season_df.season_id, y=dec_rental_earned, mode='lines+markers',  name='dec rental (payment-fees)')
    trace5 = go.Scatter(x=season_df.season_id, y=dec_rental_payed, mode='lines+markers',  name='dec rental (cost-refund)')
    trace6 = go.Scatter(x=season_df.season_id, y=dec_tournament, mode='lines+markers',  name='dec tournament (prize-entry)')
    trace7 = go.Scatter(x=season_df.season_id, y=dec_total, mode='lines+markers',  name='dec total (earnings-payments)')

    fig.add_trace(trace1)
    fig.add_trace(trace2)
    fig.add_trace(trace3)
    fig.add_trace(trace4)
    fig.add_trace(trace5)
    fig.add_trace(trace6)
    fig.add_trace(trace7)

    fig.update_layout(
        paper_bgcolor=PAPER_BGCOLOR,
        plot_bgcolor=PLOT_BGCOLOR,
        font=TEXT_FONT,

        legend=dict(
            x=0,
            y=1,
            font=dict(
                family="Courier",
                size=12,
                color="black"
            ),
            bgcolor="LightSteelBlue",
            bordercolor="Black",
            borderwidth=2
        ),
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor=GRID_COLOR,
            tickvals=season_df.season_id,
        ),

        yaxis=dict(
            title="earnings",
            gridcolor="gray",
            gridwidth=1,
            nticks=50,
            side="right"
        ),
    )

    # fig.show()
    fig.write_image("output\\3_season_stats_earnings.png", width=IMAGES_WIDTH, height=IMAGES_HEIGHT)
