from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'DiceDiceBaby_single_fixed_two_rolls'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 3
    endowment = 0


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    rev_num = models.IntegerField(label= "PLease enter the number you wish to report for your revenue", min=1, max=6)
    charity_num = models.IntegerField(label="Please enter the number you wish to report for your charity payment", min=1, max=6)
    rev_earn = models.CurrencyField()
    charity_earn = models.CurrencyField()
    donation = models.IntegerField(inital=0)
    total_donation = models.CurrencyField()


# PAGES
class Instructions(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

class Waiting(WaitPage):
    pass

class RevPage(Page):
    form_model = 'player'
    form_fields = ['rev_num']

    timeout_seconds = 60

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
                p.charity_earn = p.charity_num * 2
                p.donation = 10 - (p.charity_num * 2)

        for p in players:
            if p.round_number == 1:
                p.payoff = C.endowment + p.charity_earn + p.rev_earn
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

#Rev page first
page_sequence = [Instructions, Waiting, RevPage, RevWait, CharityPage, CharityWait, Results, PostSurvey]
#Charity page first
#page_sequence = [Instructions, Waiting, CharityPage, CharityWait, RevPage, RevWait, Results, PostSurvey]