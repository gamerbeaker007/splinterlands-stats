import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.static_values_enum import Leagues

TEXT_FONT = dict(
    family="sans serif",
    size=14,
    color="floralwhite"
)

PAPER_BGCOLOR = 'rgba(100,100,100,255)'
PLOT_BGCOLOR = 'rgba(0,0,0,0)'
GIRD_COLOR = 'rgba(255,255,255,255)'


def plot_season_stats_rating(season_df):
    fig = go.Figure()
    trace1 = go.Scatter(x=season_df.season_id, y=season_df.max_rating, mode='lines',  name='max_rating')
    trace2 = go.Scatter(x=season_df.season_id, y=season_df.rating, mode='lines', name='end rating')
    fig.add_trace(trace1)
    fig.add_trace(trace2)
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor=GIRD_COLOR)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor=GIRD_COLOR)

    fig.update_layout(
        paper_bgcolor=PAPER_BGCOLOR,
        plot_bgcolor=PLOT_BGCOLOR,
        font=TEXT_FONT,

        yaxis1=dict(
            title="rating",
        ),
    )

    # fig.show()
    fig.write_image("output\\1_season_stats_rating.png", width=800, height=600)


def plot_season_stats_battles(season_df):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    trace3 = go.Scatter(x=season_df.season_id, y=season_df.win_pct, mode='lines+markers', name='win percentage')
    trace4 = go.Scatter(x=season_df.season_id, y=season_df.battles, mode='lines', name='battles')
    trace5 = go.Scatter(x=season_df.season_id, y=season_df.wins, mode='lines', name='wins')
    fig.add_trace(trace3, secondary_y=True)
    fig.add_trace(trace4)
    fig.add_trace(trace5)
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor=GIRD_COLOR)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor=GIRD_COLOR)

    fig.update_layout(
        paper_bgcolor=PAPER_BGCOLOR,
        plot_bgcolor=PLOT_BGCOLOR,
        font=TEXT_FONT,

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
    fig.write_image("output\\2_season_stats_battles.png", width=800, height=600)


def plot_season_stats_league(season_df):
    fig = go.Figure()
    trace6 = go.Bar(x=season_df.season_id, y=season_df.league, name='end league')
    trace7 = go.Bar(x=season_df.season_id, y=season_df.max_league, name='max_league')
    fig.add_trace(trace6)
    fig.add_trace(trace7)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)

    fig.update_layout(
        paper_bgcolor=PAPER_BGCOLOR,
        plot_bgcolor=PLOT_BGCOLOR,
        font=TEXT_FONT,
        yaxis=dict(
            showgrid=False,
            title="league",
            tickvals=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
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
    fig.write_image("output\\3_season_stats_league.png", width=1920, height=1080)


def plot_season_stats_earnings(season_df):
    fig = go.Figure()
    credits_earned = season_df.credits_quest_rewards + season_df.credits_season_rewards
    sps_earned = season_df.sps_claim_staking_rewards + season_df.sps_token_award
    dec_earned = season_df.dec_reward + season_df.dec_quest_rewards + season_df.dec_season_rewards
    dec_rental_earned = season_df.dec_rental_payment + season_df.dec_rental_payment_fees
    dec_rental_payed = season_df.dec_market_rental + season_df.dec_rental_refund
    dec_tournament = season_df.dec_tournament_prize + season_df.dec_enter_tournament
    dec_total = dec_earned + dec_rental_earned + dec_rental_payed + dec_tournament
    trace1 = go.Scatter(x=season_df.season_id, y=credits_earned, mode='lines',  name='credits (quest + season reward)')
    trace2 = go.Scatter(x=season_df.season_id, y=sps_earned, mode='lines',  name='sps (staking + token award)')
    trace3 = go.Scatter(x=season_df.season_id, y=dec_earned, mode='lines',  name='dec (ranked + quest + season)')
    trace4 = go.Scatter(x=season_df.season_id, y=dec_rental_earned, mode='lines',  name='dec rental (payment-fees)')
    trace5 = go.Scatter(x=season_df.season_id, y=dec_rental_payed, mode='lines',  name='dec rental (cost-refund)')
    trace6 = go.Scatter(x=season_df.season_id, y=dec_tournament, mode='lines',  name='dec tournament (prize-entry)')
    trace7 = go.Scatter(x=season_df.season_id, y=dec_total, mode='lines',  name='total dec balance (earnings-rental)')

    fig.add_trace(trace1)
    fig.add_trace(trace2)
    fig.add_trace(trace3)
    fig.add_trace(trace4)
    fig.add_trace(trace5)
    fig.add_trace(trace6)
    fig.add_trace(trace7)
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor=GIRD_COLOR)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor=GIRD_COLOR)

    fig.update_layout(
        paper_bgcolor=PAPER_BGCOLOR,
        plot_bgcolor=PLOT_BGCOLOR,
        font=TEXT_FONT,

        yaxis1=dict(
            title="earnings",
        ),
    )

    # fig.show()
    fig.write_image("output\\4_season_stats_earnings.png", width=800, height=600)
