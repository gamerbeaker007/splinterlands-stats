

def print_season_post(username, season_df, last_season_cards_purchase):
    last_season = season_df.iloc[season_df.season.idxmax()]
    print_blog = """
# """ + str(last_season.season_name) + """ of (""" + str(username) + """): 

# Introduction:
This is an first implementation of my status reporting tool

""" + str(get_splinterlands_divider()) + """ 


Season overall stats
|||
|-|-|
|_1_|_2_|
|_3_|_4_|

""" + str(get_splinterlands_divider()) + """ 

# Last Season
""" + str(get_last_season_statistics_table(last_season)) + """

""" + str(get_splinterlands_divider()) + """ 

## Earnings and costs:
### Earnings 
""" + str(get_last_season_earnings_table(last_season)) + """

### Costs
""" + str(get_last_season_costs_table(last_season)) + """

""" + str(get_splinterlands_divider()) + """ 

## Cards Bought
""" + str(get_card_table(last_season_cards_purchase)) + """ 

## Cards Sold
TODO

## Cards Earned
TODO

""" + str(get_splinterlands_divider()) + """ 

## Closing notes 
This report is generated with the splinterstats tool from @beaker007 [git-repo](https://github.com/gamerbeaker007/splinterlands-stats). 
Any comment/remarks/errors pop me a message on peakd.   
If you like the content consider adding @beaker007 as beneficiaries of you post created with this tool. 
(images/benficiaries.png)


If you are not already playing splinterlands consider using my referral link [beaker007](https://splinterlands.com?ref=beaker007).

Thx all for readin

""" + str(get_splinterlands_logo_centered())

    print(print_blog)


def get_last_season_statistics_table(last_season):
    result = "| Statistic |  # | \n"
    result += "| - | - | \n"
    result += "| Rank | " + str(last_season['rank']) + " | \n"
    result += "| Rating | " + str(last_season.rating) + " - " + str(last_season.league_name) + " | \n"
    result += "| Rating High | " + str(last_season.max_rating) + " | \n"
    result += "| Ratio (Win/Loss) | " + str(round(last_season.wins/(last_season.battles-last_season.wins), 2)) + " (" + str(last_season.wins) + "/" + str(last_season.battles-last_season.wins) + ") |\n"
    result += "| Win PCT (Wins/battles * 100) | " + str(round(last_season.win_pct, 2)) + " (" + str(last_season.wins) + "/" + str(last_season.battles) + ") |\n"
    result += "| Longest Streak | " + str(last_season.longest_streak) + " |\n"
    return result


def get_last_season_costs_table(last_season):
    result = "| Costs |  # |\n"
    result += "| - | - |\n"
    result += "| DEC rental fees | " + str(round(last_season.dec_rental_payment_fees, 3)) + " |\n"
    result += "| DEC tournament entry prize | " + str(round(last_season.dec_enter_tournament, 3)) + " |\n"
    result += "| DEC rental payment | " + str(round(last_season.dec_market_rental, 3)) + " |\n"
    result += "| DEC market buy | " + str(round(last_season.dec_buy_market_purchase, 3)) + " |\n"
    return result


def get_last_season_earnings_table(last_season):
    result = "| Earnings |  # | \n"
    result += "| - | - |\n"
    result += "| Credits quest rewards | " + str(round(last_season.credits_quest_rewards, 3)) + " |\n"
    result += "| Credits season_rewards | " + str(round(last_season.credits_season_rewards, 3)) + " |\n"
    result += "| DEC battle rewards | " + str(round(last_season.dec_reward, 3)) + " |\n"
    result += "| DEC quest rewards | " + str(round(last_season.dec_quest_rewards, 3)) + " |\n"
    result += "| DEC season_rewards | " + str(round(last_season.dec_season_rewards, 3)) + " |\n"
    result += "| DEC tournament rewards | " + str(round(last_season.dec_tournament_prize, 3)) + " |\n"
    result += "| DEC rental rewards | " + str(round(last_season.dec_rental_payment, 3)) + " |\n"
    result += "| DEC market sell | " + str(round(last_season.dec_sell_market_purchase, 3)) + " |\n"
    return result


def get_card_table(last_season_cards_purchase):
    base_card_url = "https://d36mxiodymuqjm.cloudfront.net/cards_by_level/"
    if len(last_season_cards_purchase.index) > 5:
        result = "| | | | | |\n"
        result += "|-|-|-|-|-|\n"
    else:
        # print in one row
        table_row = "|"
        for i in range(0, len(last_season_cards_purchase.index)):
            table_row += " |"
        result = table_row + "\n" + table_row.replace(" ", "-") + "\n"

    result += "|"
    for index, card in last_season_cards_purchase.iterrows():
        if index > 0 and index % 5 == 0:
            result += "\n"
        gold_str = ""
        gold_str = "_gold" if gold_str else ""
        card_image_url = str(base_card_url) + str(card.edition_name) + "/" + str(card.card_name).replace(" ", "%20") + "_lv1" + gold_str +".png"
        result += "" + str(card_image_url) + " |"
    return result


def get_splinterlands_logo_centered():
    return "<center>https://d36mxiodymuqjm.cloudfront.net/website/splinterlands_logo.png</center>\n"


def get_splinterlands_divider():
    return "https://images.hive.blog/0x0/https://files.peakd.com/file/peakd-hive/mvl2304/EoARyG6neMCRDGfUcgEf6LMGhAAqKXL2Ty8fWffLs6p3FWfLLQeBs9oT6MJ6HUPuq4M.png"
