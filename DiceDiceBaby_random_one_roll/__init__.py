from otree.api import *
import random

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'DiceDiceBaby_random_one_roll'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    dice_roll = models.IntegerField()
    chosen_nums = models.IntegerField()
    charity_nums = models.IntegerField()

class Player(BasePlayer):
    chosen_num = models.IntegerField(label="What is the revenue number?", min=1, max=6)
    charity_num = models.IntegerField(label="What is the charity number?", min=1, max=6)
    first_num = models.IntegerField()
    second_num = models.IntegerField()
    Age = models.IntegerField(label="Please choose your age range:", choices= [[1,'>18'], [2, '18-25'], [3, '25-35'], [4, '35-45'], [5, '45<'],])
    Gender = models.StringField(label= "Please choose your gender:", choices=['Male', 'Female', 'Non-Binary', 'Prefer Not To Answer'])
    School = models.StringField(label="Please choose your highest level of education attained", choices=['Less than highschool', 'High School', 'Bachelor/Associates Degree', 'Masters', 'Phd', 'Prefer Not To Answer'])
    Work_actual = models.StringField(label="What is the highest level of employment you have reached?", choices=['Entry-level', 'Manager', 'Director', 'Vice-President', 'Chief Executive', 'Not Applicable'])
    Work_hypo = models.StringField(label="What is the highest level of employment you aspire to", choices=['Entry-level', 'Manager', 'Director', 'Vice-President', 'Chief Executive', 'Not Applicable'])


# Functions
def creating_session(session):
    for groups in session.get_groups():
        groups.dice_roll = random.randint(1, 6)

# PAGES
class Instructions(Page):
    pass

class WaitingPage(WaitPage):
    pass

class RollWithIt(Page):
    timeout_seconds = 30

    def vars_for_template(player: Player):
        group=player.group
        video_filename = f'Dice.{group.dice_roll}.mp4'
        return {
            'video_filename': video_filename,
        }

class RevPage(Page):
    timeout_seconds = 180

    form_model = 'player'
    form_fields = ['chosen_num']

    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.chosen_num = 6

class RevWaitPage(WaitPage):
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

class CharityPage(Page):
    timeout_seconds = 180

    form_model = 'player'
    form_fields = ['charity_num']

    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.charity_num = 6

class CharityWaitPage(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        players = group.get_players()
        total_charity = sum(p.charity_num for p in players)*100
        average = total_charity / len(players)
        group.charity_nums = total_charity

        for p in players:
            if p.charity_num == 6:
                p.second_num = 0
            elif p.charity_num*100 == average:
                p.second_num = p.chosen_num*100
            else:
                p.second_num = 0

        for p in group.get_players():
            p.payoff = p.first_num + p.second_num

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


page_sequence = [Instructions, WaitingPage, RollWithIt, WaitingPage, RevPage, RevWaitPage, CharityPage, CharityWaitPage, Results, PostSurvey]
