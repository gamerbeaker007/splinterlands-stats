import os
import kaleido #required

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.static_values_enum import Leagues

IMAGES_HEIGHT = 720
IMAGES_WIDTH = 1280

PAPER_BGCOLOR = 'rgba(35,35,35,255)'
PLOT_BGCOLOR = 'rgba(35,35,35,255)'
GRID_COLOR = 'rgba(170,170,170,255)'

TEXT_FONT = dict(
    family="sans serif",
    size=14,
    color=GRID_COLOR,
)


def plot_season_stats_rating(season_df, output_dir, mode):
    season_df = season_df.sort_values(by=['season'])

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    trace1 = go.Scatter(x=season_df.season,
                        y=season_df.rating,
                        mode='lines+markers',
                        name='end rating',
                        line=dict(color='firebrick', width=2),
                        )
    trace2 = go.Bar(x=season_df.season,
                    y=season_df.rating,
                    showlegend=False,
                    name='not displayed ony to create secondary axis',
                    opacity=0,
                    )

    trace3 = go.Bar(x=season_df.season,
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
            zerolinecolor=GRID_COLOR,
            tickvals=season_df.season,
        ),

        yaxis2=dict(
            zerolinecolor=GRID_COLOR,
            showgrid=True,
            title="rating",
            gridcolor=GRID_COLOR,
            gridwidth=1,
            nticks=25,
            range=[0, season_df.rating.max() * 1.05]
        ),
        yaxis=dict(
            zeroline=False,
            showgrid=False,
            title="league",
            range=[0, season_df.rating.max() * 1.05],
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
    print(kaleido.__version__)
    print("before writing image plot_season_stats_rating")
    fig.write_image(os.path.join(output_dir, "1_season_stats_rating_" + str(mode.value) + ".png"), width=IMAGES_WIDTH,
                    height=IMAGES_HEIGHT)
    print("after writing image plot_season_stats_rating")


def plot_season_stats_battles(season_df, output_dir, mode):
    season_df = season_df.sort_values(by=['season'])

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    trace3 = go.Scatter(x=season_df.season,
                        y=season_df.win_pct,
                        mode='lines+markers',
                        name='win percentage')
    trace4 = go.Scatter(x=season_df.season,
                        y=season_df.battles,
                        mode='lines+markers',
                        name='battles')
    trace5 = go.Scatter(x=season_df.season,
                        y=season_df.wins,
                        mode='lines+markers',
                        name='wins')
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
            tickvals=season_df.season,
        ),
        yaxis1=dict(
            zerolinecolor=GRID_COLOR,
            showgrid=False,
            range=[0, season_df.battles.max() + 20],
            title="battles",
        ),
        yaxis2=dict(
            zerolinecolor=GRID_COLOR,
            showgrid=False,
            overlaying='y',
            side='right',
            anchor='x2',
            range=[0, 100],
            title='win (%)'),
    )
    # fig.show()
    print("before writing image plot_season_stats_battles")
    fig.write_image(os.path.join(output_dir, "2_season_stats_battles_" + str(mode.value) + ".png"), width=IMAGES_WIDTH,
                    height=IMAGES_HEIGHT)
    print("after writing image plot_season_stats_battles")


def check_data_consistency(season_df, columns):
    for column in columns:
        if column not in season_df:
            season_df[column] = season_df.get(column, 0)
    return season_df
    pass


def plot_season_stats_earnings(season_df, output_dir="", skip_zeros=False):
    season_df = season_df.sort_values(by=['season']).fillna(0)

    # Data consistency
    columns = ['dec_reward',
               'dec_quest_rewards',
               'dec_season_rewards',
               'dec_rental_payment',
               'dec_rental_payment_fees',
               'dec_market_rental',
               'dec_rental_refund',
               'dec_tournament_prize',
               'dec_enter_tournament',
               'dec_modern_leaderboard_prizes',
               'dec_wild_leaderboard_prizes',
               'dec_market_fees',
               'dec_market_list_fee',
               'sps_claim_staking_rewards',
               'sps_token_award',
               'sps_tournament_prize',
               'sps_token_transfer_multi',
               'sps_enter_tournament',
               'sps_modern',
               'sps_wild',
               'sps_focus',
               'sps_season',
               'sps_brawl',
               'sps_land',
               'sps_nightmare',
               'merits_quest_rewards',
               'merits_season_rewards',
               'merits_brawl_prize']
    check_data_consistency(season_df, columns)

    dec_earned = season_df.dec_reward \
                 + season_df.dec_quest_rewards \
                 + season_df.dec_season_rewards \
                 + season_df.dec_modern_leaderboard_prizes \
                 + season_df.dec_wild_leaderboard_prizes

    dec_rental_earned = season_df.dec_rental_payment + season_df.dec_rental_payment_fees
    dec_rental_payed = season_df.dec_market_rental + season_df.dec_rental_refund
    dec_market_fees = season_df.dec_market_list_fee
    dec_tournament = season_df.dec_tournament_prize + season_df.dec_enter_tournament

    sps_earned = season_df.sps_claim_staking_rewards + season_df.sps_token_award
    sps_tournament = season_df.sps_tournament_prize + season_df.sps_token_transfer_multi + season_df.sps_enter_tournament
    sps_battle_earning = season_df.sps_modern + season_df.sps_wild + season_df.sps_focus + season_df.sps_season + season_df.sps_brawl
    sps_rewards = season_df.sps_land + season_df.sps_nightmare

    sps_total = sps_earned + sps_tournament + sps_battle_earning + sps_rewards
    dec_total = dec_earned + dec_rental_earned + dec_rental_payed + dec_tournament + dec_market_fees
    merits_total = season_df.merits_quest_rewards + season_df.merits_season_rewards + season_df.merits_brawl_prize

    # credits_earned = season_df.credits_quest_rewards + season_df.credits_season_rewards

    # trace1 = go.Scatter(x=season_df.season, y=credits_earned, mode='lines+markers',  name='credits (quest + season reward)')
    # trace2 = go.Scatter(x=season_df.season, y=sps_earned, mode='lines+markers',  name='sps (staking + token award)')
    # trace3 = go.Scatter(x=season_df.season, y=dec_earned, mode='lines+markers',  name='dec (ranked + quest + season)')
    # trace4 = go.Scatter(x=season_df.season, y=dec_rental_earned, mode='lines+markers',  name='dec rental (payment-fees)')
    # trace5 = go.Scatter(x=season_df.season, y=dec_rental_payed, mode='lines+markers',  name='dec rental (cost-refund)')
    # trace6 = go.Scatter(x=season_df.season, y=dec_tournament, mode='lines+markers',  name='dec tournament (prize-entry)')

    trace7 = go.Scatter(x=season_df.season,
                        y=dec_total,
                        mode='lines+markers',
                        name='DEC total (earnings - payments)',
                        line=dict(color='royalblue'))

    trace8 = go.Scatter(x=season_df.season,
                        y=merits_total,
                        mode='lines+markers',
                        name='MERITS  total (earnings)',
                        line=dict(color='red', width=2))
    trace9 = go.Scatter(x=season_df.season,
                        y=sps_total,
                        mode='lines+markers',
                        name='SPS total (earnings - payments)',
                        line=dict(color='lightgreen', width=2))

    titles = ["", "", ""]
    if not skip_zeros:
        titles = ["DEC", "MERITS", "SPS"]
        rows = 3
        fig = make_subplots(rows=rows, cols=1)
        fig.add_trace(trace7, row=1, col=1)
        fig.add_trace(trace8, row=2, col=1)
        fig.add_trace(trace9, row=3, col=1)
    else:
        total_rows = 0
        if dec_total.sum() > 0:
            total_rows += 1
        if merits_total.sum() > 0:
            total_rows += 1
        if sps_total.sum() > 0:
            total_rows += 1

        fig = make_subplots(rows=total_rows, cols=1)
        rows = 0
        if dec_total.sum() > 0:
            titles[rows] = "DEC"
            rows += 1
            fig.add_trace(trace7, row=rows, col=1)
        if merits_total.sum() > 0:
            titles[rows] = "MERITS"
            rows += 1
            fig.add_trace(trace8, row=rows, col=1)
        if sps_total.sum() > 0:
            titles[rows] = "SPS"
            rows += 1
            fig.add_trace(trace9, row=rows, col=1)

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
            tickvals=season_df.season,
        ),
        yaxis=dict(
            zerolinecolor=GRID_COLOR,
            gridcolor=GRID_COLOR,
            title=titles[0],
            side="right",
        ),

        xaxis2=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor=GRID_COLOR,
            tickvals=season_df.season,
        ),
        yaxis2=dict(
            zerolinecolor=GRID_COLOR,
            gridcolor=GRID_COLOR,
            title=titles[1],
            side="right"
        ),

        xaxis3=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor=GRID_COLOR,
            tickvals=season_df.season,
        ),
        yaxis3=dict(
            zerolinecolor=GRID_COLOR,
            gridcolor=GRID_COLOR,
            title=titles[2],
            side="right"
        ),
    )

    # fig.show()

    print("before writing image plot_season_stats_earnings")
    fig.write_image(os.path.join(output_dir, "3_season_stats_earnings.png"), width=IMAGES_WIDTH, height=480 * rows)
    print("after writing image plot_season_stats_earnings")


def plot_season_battle_history(battle_history, output_dir, mode):
    fig = go.Figure()

    title = "Battle rating history: " + str(mode.value) + " Max last 50 battles (Only ranked battles)"
    trace1 = go.Scatter(x=battle_history.index,
                        y=battle_history.rating,
                        mode='lines+markers',
                        name=str(mode.value) + " - Rating")

    fig.add_trace(trace1)
    fig.update_layout(
        paper_bgcolor=PAPER_BGCOLOR,
        plot_bgcolor=PLOT_BGCOLOR,
        font=TEXT_FONT,
        title=title,
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
            # tickvals=season_df.season,
        ),

        yaxis=dict(
            title="rating",
            gridcolor="gray",
            gridwidth=1,
            nticks=50,
            side="right"
        ),
    )

    # fig.show()
    fig.write_image(os.path.join(output_dir, "4_season_battle_history_" + str(mode.value) + ".png"), width=IMAGES_WIDTH,
                    height=IMAGES_HEIGHT)
