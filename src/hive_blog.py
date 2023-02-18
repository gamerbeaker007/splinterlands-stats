import os

import pandas as pd

credit_icon = "![credit.png](https://images.hive.blog/20x0/https://files.peakd.com/file/peakd-hive/beaker007/AK3iY7Tb28oEV8oALeHvUbBpKjWxvADTHcaqtPSL4C2YzcJ4oZLp36MAiX3qGNw.png)"
dec_icon = "![dec.png](https://images.hive.blog/20x0/https://files.peakd.com/file/peakd-hive/beaker007/AJoDPJLp3GXfJPTZijeTGTaHE5K7vzdhCXUedhPRnp6kKhanQnpfwzfnemFdz2x.png)"
sps_icon = "![sps.png](https://images.hive.blog/20x0/https://files.peakd.com/file/peakd-hive/beaker007/AKNLw1pd6ryatb2Rg9VHbWEWWUMupgMEtxYsJyxckcGH1Hb7YoxC1cFdNv37tW3.png)"
voucher_icon = "![voucher.png](https://images.hive.blog/20x0/https://files.peakd.com/file/peakd-hive/beaker007/Eo8RPwT4kQnGyvkNp9Vx1kLpFYYVhKSy88Fsy7YrAStKwrHCRX6GNvhywGxPbQpW2bu.png)"
merits_icon = "![merits.png](https://images.hive.blog/20x0/https://d36mxiodymuqjm.cloudfront.net/website/icons/img_merit_256.png)"

def print_season_post(username,
                      season_balances,
                      season_battles_wild,
                      season_battles_modern,
                      last_season_market_history,
                      purchases_cards,
                      sold_cards,
                      last_season_rewards,
                      tournaments_info,
                      output_dir=""):
    last_season = season_balances.loc[(season_balances.season_id == season_balances.season_id.max())].iloc[0]
    last_season_wild_battles = season_battles_wild.loc[(season_battles_wild.season_id == last_season.season_id)]
    last_season_modern_battles = season_battles_modern.loc[(season_battles_modern.season_id == last_season.season_id)]

    last_season_market_history_purchases = None
    last_season_market_history_sales = None
    if not last_season_market_history.empty:
        last_season_market_history_purchases = last_season_market_history[(last_season_market_history.purchaser == username)]
        last_season_market_history_sales = last_season_market_history[(last_season_market_history.seller == username)]

    if not last_season_rewards.empty:
        reward_cards = last_season_rewards[(last_season_rewards['type'] == 'reward_card')]
    else:
        reward_cards = last_season_rewards
    # print("########################################## BLOG STARTS HERE ##########################")
    print_blog = """
# Splinterlands season """ + str(last_season.season) + """ of (""" + str(username) + """): 

https://images.hive.blog/0x0/https://files.peakd.com/file/peakd-hive/beaker007/23xL2wuMjBE9nsXndxmCoPcGJARoydfwp52UTXVez31FnNbXKtkBqVx3eUBmybtD6L8J6.gif


<br><br><br>
![Season summary divider.png](https://files.peakd.com/file/peakd-hive/beaker007/23tSKXK2kCpyZXosK34FeU6MPbw4RGCrrs7TY1tgy4k5Lgndj2JNPEbpjr8JAgQ7kW8v1.png)

# <div class="phishy"><center>Season Summery</center></div>


## <div class="phishy"><center>Season overall stats and history</center></div>

### Modern

### Wild

### Earnings
 


<br><br>
![Season result divider.png](https://files.peakd.com/file/peakd-hive/beaker007/23tGwQHB4Z1zXu1MnXFvSF7REdndP7Gu67aQgWuwp9VoWurqjvGq81w2M6WkfCtovhXo4.png)
# <div class="phishy"><center>Last Season</center></div>
""" + str(get_last_season_statistics_table(last_season_wild_battles, last_season_modern_battles)) + """


<br><br>
![tournament divider1.png](https://files.peakd.com/file/peakd-hive/beaker007/23u5vZxRCDsEy53q1Rd2sXkXvnAg94fBPj2kCVNoPnjVDiyQfiPecgCJMvoSdqwe4vjQp.png)

## <div class="phishy"><center>Tournaments</center></div>
""" + str(get_tournament_info(tournaments_info)) + """

<br><br>
![Earnings divider.png](https://files.peakd.com/file/peakd-hive/beaker007/23u5tAfbYKhy3zti8o5cVxxgE2LfnjkAV4xZtm1CLAqpJL9zzEF67C7Ec8Tx6b7odFvvK.png)
## <div class="phishy"><center>Earnings and costs</center></div>
""" + str(get_last_season_earnings_table(last_season)) + """

## <div class="phishy"><center>Costs</center></div>
""" + str(get_last_season_costs_table(last_season)) + """

<br><br>
![Card Market divider.png](https://files.peakd.com/file/peakd-hive/beaker007/23tGyBstuQdzC1Pjv1CiAvt9S3W6sfo5qzCTa6Uv2mQTpfHkwkQ89YxncGYmqsrpynjEv.png)

## <div class="phishy"><center>Cards Purchased</center></div>
""" + str(get_card_table(last_season_market_history_purchases)) + """ 

# EXPERIMENTAL
""" + str(get_card_table(purchases_cards)) + """ 


## <div class="phishy"><center>Cards Sold</center></div>
""" + str(get_card_table(last_season_market_history_sales)) + """ 

# EXPERIMENTAL
Note that only card that are listed and sold in this season are displayed here.
""" + str(get_card_table(sold_cards)) + """ 


## <div class="phishy"><center>Cards Earned</center></div>
""" + str(get_card_table(reward_cards)) + """

## <div class="phishy"><center>Potions/Packs earned</center></div>
""" + str(get_rewards_potion_packs_table(last_season_rewards)) + """


<br><br>
![Closing notes divider.png](https://files.peakd.com/file/peakd-hive/beaker007/23tSMhwJoyukZ42QAed1tFdaMc2XGwQZXAoTga9AByndMur5RT4oj5rMFeNJXwBeXr4tP.png)

## <div class="phishy"><center>Closing notes</center></div>
This report is generated with the splinterstats tool from @beaker007 [git-repo](https://github.com/gamerbeaker007/splinterlands-stats). 
Any comment/remarks/errors pop me a message on peakd.   
If you like the content, consider adding @beaker007 as beneficiaries of your post created with the help of this tool. 
https://images.hive.blog/0x0/https://files.peakd.com/file/peakd-hive/beaker007/23tkhySrnBbRV3iV2aD2jH7uuYJuCsFJF5j8P8EVG1aarjqSR7cRLRmuTDhji5MnTVKSM.png


If you are not already playing splinterlands consider using my referral link [beaker007](https://splinterlands.com?ref=beaker007).

Thx all for reading

""" + str(get_splinterlands_logo_centered())

    text_file = open(os.path.join(output_dir, "post.txt"), "w")
    text_file.write(print_blog)
    text_file.close()
    print("Post can be found in file: " + str(text_file.name))
    # print(print_blog)


def get_last_season_statistics_table(last_season_wild_battles, last_season_modern_battles):
    if not last_season_wild_battles.empty:
        last_season_wild_battles = last_season_wild_battles.iloc[0]
        wild_league = last_season_wild_battles.league.astype(int)
        wild_battles = last_season_wild_battles.battles
        wild_rank = last_season_wild_battles['rank']
        wild_rating = last_season_wild_battles.rating
        wild_league_name = last_season_wild_battles.league_name
        wild_max_rating = last_season_wild_battles.max_rating
        wild_win = last_season_wild_battles.wins
        wild_win_pct = round(last_season_wild_battles.win_pct, 2)
        wild_longest_streak = last_season_wild_battles.longest_streak
        wild_ratio = round(wild_win/(wild_battles-wild_win), 2)
        wild_loss = wild_battles-wild_win
    else:
        wild_league = 0
        wild_league_name = "NA"
        wild_battles = "NA"
        wild_rank = "NA"
        wild_rating = "NA"
        wild_max_rating = "NA"
        wild_win = "NA"
        wild_win_pct = "NA"
        wild_longest_streak = "NA"
        wild_ratio = "NA"
        wild_loss = "NA"

    if not last_season_modern_battles.empty:
        last_season_modern_battles = last_season_modern_battles.iloc[0]
        modern_league = last_season_modern_battles.league.astype(int)
        modern_battles = last_season_modern_battles.battles
        modern_rank = last_season_modern_battles['rank']
        modern_rating = last_season_modern_battles.rating
        modern_league_name = last_season_modern_battles.league_name
        modern_max_rating = last_season_modern_battles.max_rating
        modern_win = last_season_modern_battles.wins
        modern_win_pct = round(last_season_modern_battles.win_pct, 2)
        modern_longest_streak = last_season_modern_battles.longest_streak
        modern_ratio = round(modern_win/(modern_battles-modern_win), 2)
        modern_loss = modern_battles-modern_win
    else:
        modern_league = 0
        modern_league_name = "NA"
        modern_battles = "NA"
        modern_rank = "NA"
        modern_rating = "NA"
        modern_max_rating = "NA"
        modern_win = "NA"
        modern_win_pct = "NA"
        modern_longest_streak = "NA"
        modern_ratio = "NA"
        modern_loss = "NA"

    wild_league_logo = "https://images.hive.blog/75x0/https://d36mxiodymuqjm.cloudfront.net/website/icons/leagues/wild_150/league_" + str(wild_league) + ".png"
    modern_league_logo = "https://images.hive.blog/75x0/https://d36mxiodymuqjm.cloudfront.net/website/icons/leagues/modern_150/league_" + str(modern_league) + ".png"
    extra_space = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
    result = "| Statistic |  " + wild_league_logo + "<br>" + extra_space + "Wild| " + modern_league_logo + "<br>" + extra_space + "Modern | \n"
    result += "| - | - | - |\n"
    result += "| Battles | " + str(wild_battles) + " | "
    result += str(modern_battles) + " | \n"
    result += "| Rank | " + str(wild_rank) + " | "
    result += str(modern_rank) + " | \n"
    result += "| Rating | " + str(wild_rating) + " - " + str(wild_league_name) + " | "
    result += str(modern_rating) + " - " + str(modern_league_name) + " | \n"
    result += "| Rating High | " + str(wild_max_rating) + " | "
    result += str(modern_max_rating) + " | \n"
    result += "| Ratio (Win/Loss) | " + str(wild_ratio) + " (" + str(wild_win) + "/" + str(wild_loss) + ") |"
    result += str(modern_ratio) + " (" + str(modern_win) + "/" + str(modern_loss) + ") |\n"
    result += "| Win PCT (Wins/battles * 100) | " + str(wild_win_pct) + " (" + str(wild_win) + "/" + str(wild_battles) + ") |"
    result += str(modern_win_pct) + " (" + str(modern_win) + "/" + str(modern_battles) + ") |\n"
    result += "| Longest Streak | " + str(wild_longest_streak) + " |"
    result += str(modern_longest_streak) + " |\n"

    return result


def get_last_season_costs_table(last_season):
    result = "| Costs |  # |\n"
    result += "| - | - |\n"
    result += "| DEC rental fees | " + dec_icon + " " + str(round(last_season.dec_rental_payment_fees, 3)) + " |\n"
    result += "| DEC tournament entry fees | " + dec_icon + " " + str(round(last_season.dec_enter_tournament, 3)) + " |\n"
    result += "| SPS tournament entry fees | " + sps_icon + " " + str(round(last_season.sps_enter_tournament, 3)) + " |\n"
    result += "| DEC rental payment | " + dec_icon + " " + str(round(last_season.dec_market_rental, 3)) + " |\n"
    result += "| DEC market buy | " + dec_icon + " " + str(round(last_season.dec_buy_market_purchase, 3)) + " |\n"
    return result


def get_last_season_earnings_table(last_season):
    result = "| Earnings |  # | \n"
    result += "| - | - |\n"
    result += "| DEC rental rewards | " + dec_icon + " " + str(round(last_season.dec_rental_payment, 3)) + " |\n"
    result += "| DEC market sell | " + dec_icon + " " + str(round(last_season.dec_sell_market_purchase, 3)) + " |\n"
    result += "| DEC tournament rewards | " + dec_icon + " " + str(round(last_season.dec_tournament_prize, 3)) + " |\n"
    result += "| SPS tournament rewards | " + sps_icon + " " + str(round(last_season.sps_tournament_prize, 3)
                                                                   + round(last_season.sps_token_transfer_multi, 3)) + " |\n"
    result += "| SPS staking reward | " + sps_icon + " " + str(round(last_season.sps_claim_staking_rewards, 3)) + " |\n"
    result += "| SPS token award (pools) | " + sps_icon + " " + str(round(last_season.sps_token_award, 3)) + " |\n"
    result += "| SPS ranked battle (modern) | " + sps_icon + " " + str(round(last_season.sps_modern, 3)) + " |\n"
    result += "| SPS ranked battle (wild) | " + sps_icon + " " + str(round(last_season.sps_wild, 3)) + " |\n"
    result += "| SPS daily focus | " + sps_icon + " " + str(round(last_season.sps_focus, 3)) + " |\n"
    result += "| SPS season | " + sps_icon + " " + str(round(last_season.sps_season, 3)) + " |\n"
    result += "| SPS land | " + sps_icon + " " + str(round(last_season.sps_land, 3)) + " |\n"
    result += "| SPS nightmare (TD)  | " + sps_icon + " " + str(round(last_season.sps_nightmare, 3)) + " |\n"
    result += "| SPS brawl | " + sps_icon + " " + str(round(last_season.sps_brawl, 3)) + " |\n"
    result += "| MERITS quest reward | " + merits_icon + " " + str(round(last_season.merits_quest_rewards, 3)) + " |\n"
    result += "| MERITS season rewards | " + merits_icon + " " + str(round(last_season.merits_season_rewards, 3)) + " |\n"
    result += "| MERITS brawl prizes | " + merits_icon + " " + str(round(last_season.merits_brawl_prize, 3)) + " |\n"
    result += "| VOUCHER earned | " + voucher_icon + " " + str(round(last_season.voucher_claim_staking_rewards, 3)) + " |\n"

    return result


def get_tournament_info(tournaments_info):
    result = "|Tournament name | League | finish / entrants | wins/losses/draws | entry fee | prize |  \n"
    result += "|-|-|-|-|-|-| \n"

    if not tournaments_info.empty:
        for index, tournament in tournaments_info.iterrows():
            if tournament.finish:
                result += "| " + tournament['name']
                result += "| " + tournament.league
                result += "| " + str(int(tournament.finish)) + " / " + str(int(tournament.num_players))
                result += "| " + str(int(tournament.wins)) + " / " + str(int(tournament.losses)) + " / " + str(int(tournament.draws))
                result += "| " + tournament.entry_fee
                result += "| " + tournament.prize_qty + " " + tournament.prize_type
                result += "| \n"

        filters_sps_prizes = tournaments_info[tournaments_info.prize_type == "SPS"]
        total_sps_earned = pd.to_numeric(filters_sps_prizes[['prize_qty']].sum(1), errors='coerce').sum()

        filters_sps_entry_fee = tournaments_info[tournaments_info.entry_fee.str.contains("SPS")]
        # TODO FIX Warning here no clue how yet
        filters_sps_entry_fee[['fee_qty', 'fee_type']] = filters_sps_entry_fee.entry_fee.str.split(" ", expand=True)
        total_sps_fee = pd.to_numeric(filters_sps_entry_fee[['fee_qty']].sum(1), errors='coerce').sum()

        result += "|**Total SPS** | | | | **" + str(total_sps_fee) + "**|**" + str(total_sps_earned) + "**| \n"

    return result


def get_card_table(cards_df):
    base_card_url = "https://images.hive.blog/150x0/https://d36mxiodymuqjm.cloudfront.net/cards_by_level/"

    if cards_df is not None and len(cards_df) > 0:
        unique_card_list = cards_df.card_name.unique()
        temp = pd.DataFrame()
        for card_name in unique_card_list:
            temp = pd.concat([temp, pd.DataFrame({
                'card_name': card_name,
                'quantity_regular': len(cards_df[(cards_df['card_name'] == card_name) & (cards_df['gold'] == False)]),
                'quantity_gold':  len(cards_df[(cards_df['card_name'] == card_name) & (cards_df['gold'] == True)]),
                'edition_name': str(cards_df[(cards_df['card_name'] == card_name)].edition_name.values[0]),
            }, index=[0])], ignore_index=True)


        if len(temp.index) > 5:
            result = "| | | | | |\n"
            result += "|-|-|-|-|-|\n"
        else:
            # print all in one row
            table_row = "|"
            for i in range(0, len(temp.index)):
                table_row += " |"
            result = table_row + "\n" + table_row.replace(" ", "-") + "\n"

        result += "|"
        for index, card in temp.iterrows():
            if index > 0 and index % 5 == 0:
                result += "\n"

            if card.quantity_regular > 0:
                card_image_url = str(base_card_url) + str(card.edition_name) + "/" + str(card.card_name).replace(" ","%20") + "_lv1.png"
                result += "" + str(card_image_url) + "<br> " + str(card.quantity_regular) + "x"
            if card.quantity_gold > 0:
                card_image_url = str(base_card_url) + str(card.edition_name) + "/" + str(card.card_name).replace(" ","%20") + "_lv1_gold.png"
                result += "" + str(card_image_url) + "<br> " + str(card.quantity_gold) + "x"
            result += " |"
    else:
        result = "None"
    return result


def get_rewards_potion_packs_table(last_season_rewards):
    if not last_season_rewards.empty:
        gold_potion = "![alchemy.png](https://images.hive.blog/120x0/https://files.peakd.com/file/peakd-hive/beaker007/AK6ZKi4NWxuWbnhNc1V3k9DeqiqhTvmcenpsX5xhHUFdBGEYTMfMpsnC9aHL7R2.png)"
        legendary_potion = "![legendary.png](https://images.hive.blog/120x0/https://files.peakd.com/file/peakd-hive/beaker007/AK3gbhdHjfaQxKVM39VfeHCw25haYejvUT17E8WBgveTKY5rucpRY7AbjgsAhdu.png)"
        packs_img = "![chaosPack.png](https://images.hive.blog/120x0/https://files.peakd.com/file/peakd-hive/beaker007/Eo8M4f1Zieju9ibwbs6Tnp3KvN9Kb93HkqwMi3FqanTmV2XoNw7pmV4MbjDSxbgiSdo.png)"

        potions = last_season_rewards[(last_season_rewards['type'] == 'potion')].groupby(['potion_type']).sum()
        packs = last_season_rewards[(last_season_rewards['type'] == 'pack')].groupby(['edition']).sum()
        result = "| Legendary | Gold | Packs |\n"
        result += "|-|-|-|\n"
        result += "| " + str(legendary_potion) + "<br> " + str(potions.loc['legendary'].quantity) + "x"
        result += "| " + str(gold_potion) + "<br> " + str(potions.loc['gold'].quantity) + "x"
        if packs.empty:
            result += "| " + str(packs_img) + "<br> 0x"
        else:
            result += "| " + str(packs_img) + "<br> " + str(packs.loc[7.0].quantity) + "x"

        result += "|\n"
        return result
    else:
        return "None"


def get_splinterlands_logo_centered():
    return "<center>https://d36mxiodymuqjm.cloudfront.net/website/splinterlands_logo.png</center>\n"

