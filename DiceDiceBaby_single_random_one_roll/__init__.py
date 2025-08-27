from otree.api import *
import random


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'DiceDiceBaby_single_random_one_roll'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 2
    show_up = 0 #This is where you can add a show up fee

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    charity_num = models.IntegerField(label='Please enter your charity roll', min = 1, max = 6)
    rev_num = models.IntegerField(label= 'Please enter your revenue roll value', min = 1, max = 6)
    charity_earn = models.CurrencyField()
    rev_earn = models.CurrencyField()
    donation = models.IntegerField()
    total_donation = models.CurrencyField(initial = 0)
    roll = models.IntegerField()
    # This is all the demographic questions for the Post experiment survey
    Age = models.IntegerField(label="Please choose your age range:", choices=[[1, '>18'], [2, '18-25'], [3, '25-35'], [4, '35-45'], [5, '45<'], ])
    Gender = models.StringField(label="Please choose your gender:", choices=['Male', 'Female', 'Prefer Not To Answer'])
    School = models.StringField(label="Please choose your highest level of education attained", choices=['Less than highschool', 'High School', 'Bachelor/Associates Degree', 'Masters', 'Phd', 'Prefer Not To Answer'])
    Work_actual = models.StringField(label="What is the highest level of employment you have reached?", choices=['Entry-level', 'Manager', 'Director', 'Vice-President', 'Chief Executive', 'Not Applicable'])
    Work_hypo = models.StringField(label="What is the highest level of employment you aspire to", choices=['Entry-level', 'Manager', 'Director', 'Vice-President', 'Chief Executive','Not Applicable'])


#FUNCTIONS
def creating_session(subsession):
    for p in subsession.get_players():
        p.roll = random.randint(1,6)

# PAGES
class Instructions(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

class WaitForIt(WaitPage):
    pass

class Roll(Page):
    timeout_seconds = 15 #This is how long they can see the roll for

    def vars_for_template(player):
        video_filename= f'Dice.{player.roll}.mp4'
        return{
            'video_filename': video_filename
        }

class RevPage(Page):
    timeout_seconds = 60

    form_model = 'player'
    form_fields = ['rev_num']

    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.rev_num = 6

class RevWait(WaitPage):
    @staticmethod
    def after_all_players_arrive(group):
        for p in group.get_players():
            if p.rev_num == 6:
                p.rev_earn = 0
            else:
                p.rev_earn = p.rev_num

class CharityPage(Page):
    timeout_seconds = 60

    form_model = 'player'
    form_fields = ['charity_num']

    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.charity_num = 6

class CharityWait(WaitPage):
    @staticmethod
    def after_all_players_arrive(group):
        players = group.get_players()
        for p in players:
            if p.charity_num == 6:
                p.charity_earn = 0
                p.donation = 10
            else:
                p.charity_earn = p.charity_num*2
                p.donation = 10 - p.charity_num*2

        for p in players:
            if p.round_number == 1:
                p.payoff = C.show_up + p.charity_earn + p.rev_earn
                p.total_donation = p.donation
            else:
                p.payoff = p.charity_earn + p.rev_earn
                previous_donation = p.in_round(p.round_number-1).total_donation
                p.total_donation = previous_donation + p.donation

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

#Rev first
page_sequence = [Instructions, WaitForIt, Roll, RevPage, RevWait, CharityPage, CharityWait, Results, PostSurvey]
#charity first
#page_sequence = [Instructions, WaitForIt, Roll, CharityPage, CharityWait, RevPage, RevWait, Results, PostSurvey]
