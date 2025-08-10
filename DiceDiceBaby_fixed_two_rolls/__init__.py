from otree.api import *
import itertools



doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'DiceDiceBaby_fixed_two_rolls'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    dice_roll_1 = models.IntegerField()
    dice_roll_2 = models.IntegerField()
    chosen_nums = models.CurrencyField()
    charity_nums = models.CurrencyField()

class Player(BasePlayer):
    treatment = models.IntegerField()
    chosen_num = models.CurrencyField(label="The income value selected is: ", min=1, max=6)
    charity_num = models.CurrencyField(label="The charity value selected is: ", min=1, max=6)
    first_num = models.CurrencyField()
    second_num = models.CurrencyField()
    charity_pay = models.CurrencyField()
    Age = models.IntegerField(label="Please choose your age range:", choices= [[1,'>18'], [2, '18-25'], [3, '25-35'], [4, '35-45'], [5, '45<'],])
    Gender = models.StringField(label= "Please choose your gender:", choices=['Male', 'Female', 'Non-Binary', 'Prefer Not To Answer'])
    School = models.StringField(label="Please choose your highest level of education attained", choices=['Less than highschool', 'High School', 'Bachelor/Associates Degree', 'Masters', 'Phd', 'Prefer Not To Answer'])
    Work_actual = models.StringField(label="What is the highest level of employment you have reached?", choices=['Entry-level', 'Manager', 'Director', 'Vice-President', 'Chief Executive', 'Not Applicable'])
    Work_hypo = models.StringField(label="What is the highest level of employment you aspire to", choices=['Entry-level', 'Manager', 'Director', 'Vice-President', 'Chief Executive', 'Not Applicable'])



#functions
def creating_session(session):
    if session.round_number == 1:
        treatment_cycle = itertools.cycle(['1', '2', '3', '4'])
        for group in session.get_groups():
            treatment = next(treatment_cycle)
            group.treatment = treatment
            for p in group.get_players():
                p.treatment = group.treatment
    else:
        session.group_like_round(1)


# PAGES
class Instructions(Page):
    pass

class WaitPageIns(WaitPage):
    pass

class RollOne(Page):
    form_model = 'player'
    form_fields = ['chosen_num']

    timeout_seconds = 180

    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.chosen_num=6

class WaitPageRev(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        players = group.get_players()
        total_chosen = sum(p.chosen_num for p in players)*100
        average = total_chosen / len(players)
        group.chosen_nums = total_chosen

        for p in players:
            if p.chosen_num == 6:
                p.first_num = 0
            elif p.chosen_num*100 == average:
                p.first_num = p.chosen_num*100
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
        total_charity = sum(p.charity_num for p in players) * 100
        average = total_charity / len(players)
        group.charity_nums = total_charity

        for p in players:
            if p.charity_num * 100 == average:
                p.second_num = 1000-(p.charity_num-1)*200
            else:
                p.second_num = 0

        for p in group.get_players():
            p.payoff = p.first_num + p.second_num


class Results(Page):
    pass

class PostSurvey(Page):
    form_model = 'player'
    form_fields = ['age', 'gender', 'school', 'work_hypo', 'work_actual' ]

page_sequence = [Instructions, WaitPageIns, RollOne, WaitPageRev, RollTwo, WaitPageChar, Results, PostSurvey]
