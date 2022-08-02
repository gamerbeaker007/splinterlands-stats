
def data_migration_modern_wild(season_balances_df, output_file):
    # After modern and wild change migrate to separate file and remove battle information from the season
    if 'battles' in season_balances_df.columns:
        # backup file
        season_balances_df.to_csv(output_file + ".bak")

        # drop old battle info
        season_balances_df = season_balances_df.drop(['rank',
                                                      'adjusted_rank',
                                                      'rating',
                                                      'battles',
                                                      'wins',
                                                      'longest_streak',
                                                      'max_rating',
                                                      'league',
                                                      'max_league',
                                                      'reward_claim_tx',
                                                      'guild_id',
                                                      'guild_name',
                                                      'guild_data',
                                                      'avatar_id',
                                                      'display_name',
                                                      'title_pre',
                                                      'title_post',
                                                      'end_league_rating',
                                                      'league_name',
                                                      'max_league_name',
                                                      'win_pct'], axis=1)
        season_balances_df.to_csv(output_file)
        print("Data migration for modern and wild performed")
    return season_balances_df
