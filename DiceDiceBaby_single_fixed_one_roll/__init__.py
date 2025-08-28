from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'DiceDiceBaby_single_fixed_one_roll'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 2
    endowment = 0 #If you want a show-up payment, put it here

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    rev_num = models.IntegerField(label= "Please enter the number you wish to report for your revenue", min=1, max=6)
    charity_num = models.IntegerField(label="Please enter the number you wish to report for your charity payment", min=1, max=6)
    rev_earn = models.CurrencyField()
    charity_earn = models.CurrencyField()
    donation = models.IntegerField()
    total_donation = models.CurrencyField()
    # This is all the PostSurvey questions. You can adjust the choices here, but if you want to change
    # the choices you need to change them here, in the PostSurvey page section and on the html page
    Age = models.IntegerField(label="Please choose your age range:", choices=[[1, '>18'], [2, '18-25'], [3, '25-35'], [4, '35-45'], [5, '45<'], ])
    Gender = models.StringField(label="Please choose your gender:", choices=['Male', 'Female', 'Prefer Not To Answer'])
    School = models.StringField(label="Please choose your highest level of education attained", choices=['Less than highschool', 'High School', 'Bachelor/Associates Degree', 'Masters', 'Phd', 'Prefer Not To Answer'])
    Work_actual = models.StringField(label="What is the highest level of employment you have reached?", choices=['Entry-level', 'Manager', 'Director', 'Vice-President', 'Chief Executive','Not Applicable'])
    Work_hypo = models.StringField(label="What is the highest level of employment you aspire to", choices=['Entry-level', 'Manager', 'Director', 'Vice-President', 'Chief Executive', 'Not Applicable'])


# PAGES
class Instructions(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

class Roll(Page):
    timeout_seconds = 10 #You can change how long the roll is shown for here

class CharityPage(Page):
    timeout_seconds = 60

    form_model = 'player'
    form_fields = ['charity_num']

    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.charity_num = 6

class RevPage(Page):
    timeout_seconds = 60

    form_model = 'player'
    form_fields= ['rev_num']

    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.rev_num = 6 #If you change the payout scheme, put whatever 0 is here.
    #if you change to charity first, put the payoff section here

class RevWait(WaitPage):
    @staticmethod
    def after_all_players_arrive(group):
        for p in group.get_players():
            if p.rev_num == 6:
                p.rev_earn = 0
            else:
                p.rev_earn = p.rev_num

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
                p.donation = 10 - p.charity_num*2
#This is the payoff section
        for p in players:
            if p.round_number == 1:
                p.payoff = C.endowment + p.charity_earn + p.rev_earn
                p.total_donation = p.donation
            else:
                p.payoff = p.charity_earn + p.rev_earn
                previous_donation = p.in_round(p.round_number-1).total_donation
                p.total_donation = previous_donation + p.donation
#If you change to charity first, move it to the rev page
class Results(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS

class PostSurvey(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS

    form_model = 'player'
    form_fields = ['Age', 'Gender', 'School', 'Work_hypo', 'Work_actual']
#You can add or remove survey questions here and on the PostSurvey HTML page.
#If you remove it entirely, erase it from the page sequence
class Waiting(WaitPage):
    pass

#Rev first
page_sequence = [Instructions, Waiting, Roll, RevPage, RevWait, CharityPage, CharityWait, Results, PostSurvey]
#Charity first
#page_sequence= [Instructions, Waiting, CharityPage, CharityWait, RevPage, RevWait, Results, PostSurvey]
# if you change this, you also need to move the payoffs portion to the rev wait page