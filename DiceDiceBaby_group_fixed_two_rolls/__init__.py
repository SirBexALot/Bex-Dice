from otree.api import *
import itertools



doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'DiceDiceBaby_group_fixed_two_rolls'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 2
    show_up = 0 #Your show-up payment if you want one

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    #These are all the numbers that are the same for the whole group.
    #For a single player these become player variables
    dice_roll_1 = models.IntegerField()
    dice_roll_2 = models.IntegerField()
    #these are unneeded (also note these become the sum of the player variables so they have an s at the end)
    chosen_nums = models.CurrencyField()
    charity_nums = models.CurrencyField()
    match = models.BooleanField()
    treatment = models.IntegerField()

class Player(BasePlayer):
    treatment = models.IntegerField()
    chosen_num = models.CurrencyField(label="The income value selected is: ", min=1, max=6)
    charity_num = models.CurrencyField(label="The charity value selected is: ", min=1, max=6)
    first_num = models.CurrencyField()
    second_num = models.CurrencyField()
    total_charity = models.CurrencyField(initial = 0)
    charity = models.CurrencyField()
    #These are just the demographic survey questions
    Age = models.IntegerField(label="Please choose your age range:", choices= [[1,'>18'], [2, '18-25'], [3, '25-35'], [4, '35-45'], [5, '45<'],])
    Gender = models.StringField(label= "Please choose your gender:", choices=['Male', 'Female', 'Prefer Not To Answer'])
    School = models.StringField(label="Please choose your highest level of education attained", choices=['Less than highschool', 'High School', 'Bachelor/Associates Degree', 'Masters', 'Phd', 'Prefer Not To Answer'])
    Work_actual = models.StringField(label="What is the highest level of employment you have reached?", choices=['Entry-level', 'Manager', 'Director', 'Vice-President', 'Chief Executive', 'Not Applicable'])
    Work_hypo = models.StringField(label="What is the highest level of employment you aspire to", choices=['Entry-level', 'Manager', 'Director', 'Vice-President', 'Chief Executive', 'Not Applicable'])



#functions
#This will divide the players into 4 treatments. It can be changed easily, but needs to be changes here
#and new/changes if statements on the RollOne and RollTwo pages (used {{ elif }} / {{ end elif }}
# Can also add "and player.round_number == 1/2/3/etc" for  multiple rounds.
#Currently, I have it so players see 2,2; 2,4; 4,2; or 4,4
def creating_session(session):
    if session.round_number == 1:
        treatment_cycle = itertools.cycle(['1', '2', '3', '4'])
        for group in session.get_groups():
            treatment = next(treatment_cycle)
            group.treatment = treatment
            for player in group.get_players():
                player.treatment = treatment
    else:
        session.group_like_round(1)
        for group in session.get_groups():
            group_in_round1 = group.in_round(1)
            group.treatment = group_in_round1.treatment
            for player in group.get_players():
                player.treatment = player.in_round(1).treatment



# PAGES
class Instructions(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

class WaitPageIns(WaitPage):
    pass

class RollOne(Page):
    form_model = 'player'
    form_fields = ['chosen_num']

    timeout_seconds = 180 #choose how long you want the players to stay on the page for.
    #On the html page you can choose how long to hide the player input buttons

    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.chosen_num=6 #automatically sets the input to 6 if no input is received by the timeout.

class WaitPageRev(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        players = group.get_players()
        p1_chosen_num = players[0].chosen_num
        p2_chosen_num = players[1].chosen_num
        p3_chosen_num = players[2].chosen_num

        if p1_chosen_num == p2_chosen_num and p2_chosen_num == p3_chosen_num:
            group.match = True
        else:
            group.match = False

        for p in players:

            if group.match == True:
                if p.chosen_num == 6:
                    p.first_num = 0
                else:
                    p.first_num = p.chosen_num
            else:
                p.first_num = 0

class RollTwo(Page):
    form_model = 'player'
    form_fields = ['charity_num']

    timeout_seconds = 180

    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.charity_num=6

class WaitPageChar(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        players = group.get_players()
        p1_charity_num = players[0].charity_num
        p2_charity_num = players[1].charity_num
        p3_charity_num = players[2].charity_num

        if p1_charity_num == p2_charity_num and p2_charity_num == p3_charity_num:
            group.match = True
        else:
            group.match = False

        for p in players:
            if group.match == False:
                p.second_num = 0
                p.charity = 10
            elif p.charity_num == 6:
                p.second_num = 0
                p.charity = 10
            else:
                p.second_num = p.charity_num*2
                p.charity = 10 - p.charity_num*2

        for p in group.get_players():
            if p.round_number == 1:
                p.payoff = p.first_num + p.second_num + C.show_up
                p.total_charity = p.charity
            else:
                p.payoff = p.first_num + p.second_num
                previous_total = p.in_round(p.round_number-1).total_charity
                p.total_charity = previous_total + p.charity


class Results(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS

class PostSurvey(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS

    form_model = 'player'
    form_fields = ['Age', 'Gender', 'School', 'Work_hypo', 'Work_actual' ]

# Page sequence for REVENUE first
page_sequence = [Instructions, WaitPageIns, RollOne, WaitPageRev, RollTwo, WaitPageChar, Results, PostSurvey]

# Page sequence for CHARITY first
#page_sequence = [Instructions, WaitPageIns, RollTwo, WaitPageChar, RollOne, WaitPageRev, Results, PostSurvey]