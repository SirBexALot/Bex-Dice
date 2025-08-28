from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'DiceDiceBaby_single_fixed_two_rolls'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 3
    endowment = 0 #If you want a show-up payment, you can add it here.


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    rev_num = models.IntegerField(label= "Please enter the number you wish to report for your revenue", min=1, max=6)
    charity_num = models.IntegerField(label="Please enter the number you wish to report for your charity payment", min=1, max=6)
    rev_earn = models.CurrencyField()
    charity_earn = models.CurrencyField()
    donation = models.IntegerField(inital=0)
    total_donation = models.CurrencyField()
    # This is all the demographic questions for the Post experiment survey
    Age = models.IntegerField(label="Please choose your age range:", choices=[[1, '>18'], [2, '18-25'], [3, '25-35'], [4, '35-45'], [5, '45<'], ])
    Gender = models.StringField(label="Please choose your gender:", choices=['Male', 'Female', 'Prefer Not To Answer'])
    School = models.StringField(label="Please choose your highest level of education attained", choices=['Less than highschool', 'High School', 'Bachelor/Associates Degree', 'Masters', 'Phd', 'Prefer Not To Answer'])
    Work_actual = models.StringField(label="What is the highest level of employment you have reached?", choices=['Entry-level', 'Manager', 'Director', 'Vice-President', 'Chief Executive', 'Not Applicable'])
    Work_hypo = models.StringField(label="What is the highest level of employment you aspire to", choices=['Entry-level', 'Manager', 'Director', 'Vice-President', 'Chief Executive', 'Not Applicable'])

# PAGES
class Instructions(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1 #Only shows during round 1

class Waiting(WaitPage):
    pass

class RevPage(Page):
    form_model = 'player'
    form_fields = ['rev_num']

    timeout_seconds = 60 #If you change how long the page is shown for, change it here and update the instructions

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
            player.charity_num = 6 #This will give players 0 if they time out the page. Change it if you change the payoff scheme

class CharityWait(WaitPage):
    @staticmethod
    def after_all_players_arrive(group):
        players = group.get_players()
        for p in players:
            if p.charity_num == 6:
                p.charity_earn = 0
                p.donation = 10
            else:
                p.charity_earn = p.charity_num * 2
                p.donation = 10 - (p.charity_num * 2)
#This is the payoffs section
        for p in players:
            if p.round_number == 1:
                p.payoff = C.endowment + p.charity_earn + p.rev_earn
                p.total_donation = p.donation
            else:
                p.payoff = p.charity_earn + p.rev_earn
                previous_donation = p.in_round(p.round_number-1).total_donation
                p.total_donation = previous_donation + p.donation
#If you change the order to charity first, you have to move this to the REV page section
class Results(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS #This will just show the page during the last round early. what you show is in the HTML

class PostSurvey(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS

    form_model = 'player'
    form_fields = ['Age', 'Gender', 'School', 'Work_actual', "Work_hypo"] #change here and on PostSurvey page if you change these
    #If you remove the post survey here and have it as a separate app, erase it from the page sequence

#Rev page first
page_sequence = [Instructions, Waiting, RevPage, RevWait, CharityPage, CharityWait, Results, PostSurvey]
#Charity page first
#page_sequence = [Instructions, Waiting, CharityPage, CharityWait, RevPage, RevWait, Results, PostSurvey]