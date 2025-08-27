from otree.api import *
import random

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'DiceDiceBaby_group_random_one_roll'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 1
    show_up = 0


class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    dice_roll = models.IntegerField()
    chosen_nums = models.IntegerField()
    charity_nums = models.IntegerField()
    match = models.BooleanField()

class Player(BasePlayer):
    chosen_num = models.IntegerField(label="What is the revenue number?", min=1, max=6)
    #If you change to "tax" instead of "charity" you can just change the green text, players can't see the variable name
    charity_num = models.IntegerField(label="What is the charity number?", min=1, max=6)
    first_num = models.IntegerField()
    second_num = models.IntegerField()
    charity = models.IntegerField()
    total_charity = models.CurrencyField()
#This is all the demographic questions for the Post experiment survey
    Age = models.IntegerField(label="Please choose your age range:", choices= [[1,'>18'], [2, '18-25'], [3, '25-35'], [4, '35-45'], [5, '45<'],])
    Gender = models.StringField(label= "Please choose your gender:", choices=['Male', 'Female', 'Prefer Not To Answer'])
    School = models.StringField(label="Please choose your highest level of education attained", choices=['Less than highschool', 'High School', 'Bachelor/Associates Degree', 'Masters', 'Phd', 'Prefer Not To Answer'])
    Work_actual = models.StringField(label="What is the highest level of employment you have reached?", choices=['Entry-level', 'Manager', 'Director', 'Vice-President', 'Chief Executive', 'Not Applicable'])
    Work_hypo = models.StringField(label="What is the highest level of employment you aspire to", choices=['Entry-level', 'Manager', 'Director', 'Vice-President', 'Chief Executive', 'Not Applicable'])


# Functions
#This creates the random number for the session.
def creating_session(session):
    for groups in session.get_groups():
        groups.dice_roll = random.randint(1, 6)

# PAGES
class Instructions(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

class WaitingPage(WaitPage):
    pass

class RollWithIt(Page):
    timeout_seconds = 30 #This is how long to see the page for
    #I put 30 seconds for fun, you can change it. There is no "next" button so people can't skip the page

    #This will display the dice roll based on how the files are currently named.
    #If you change the names of the videos, you need to change the green text part and keep a number in the title.
    #(The number is the random dice roll)
    def vars_for_template(player: Player):
        group=player.group
        video_filename = f'Dice.{group.dice_roll}.mp4'
        return {
            'video_filename': video_filename,
        }

class RevPage(Page):
    timeout_seconds = 180 #how long you want the page to display for.
    #How long you want the formfield hidden for is on the HTML page

    form_model = 'player'
    form_fields = ['chosen_num']
#sets the payout to 0 if players don't input a numer
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.chosen_num = 6

class RevWaitPage(WaitPage):
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

class CharityPage(Page):
    timeout_seconds = 180 #change this is you want the page to be available for a different amount of time

    form_model = 'player'
    form_fields = ['charity_num']

    def before_next_page(player, timeout_happened): #This makes a timeout payout 0. If 6 isn't 0, change it.
        if timeout_happened:
            player.charity_num = 6

class CharityWaitPage(WaitPage):
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

            if group.match == True:
                if p.charity_num == 6:
                    p.charity = 10
                    p.second_num = 0
                else:
                    p.second_num = p.charity_num*2
                    p.charity = 10-p.charty_num*2
            else:
                p.second_num = 0
                p.charity = 10

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
    form_fields = ['Age', 'Gender', 'School', 'Work_actual', "Work_hypo"]

#Revenue page first
page_sequence = [Instructions, WaitingPage, RollWithIt, WaitingPage, RevPage, RevWaitPage, CharityPage, CharityWaitPage, Results, PostSurvey]
#Charity page first
#page_sequence = [Instructions, WaitingPage, RollWithIt, WaitingPage, CharityPage, CharityWaitPage, RevPage, RevWaitPage,Results, PostSurvey]