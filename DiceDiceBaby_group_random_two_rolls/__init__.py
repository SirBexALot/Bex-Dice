from otree.api import *
import random

from otree.database import BooleanField

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'DiceDiceBaby_group_random_two_rolls'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 2
    show_up = 0 #if you want any show up amount, change the 0
    #options = [2, 3, 4]

class Subsession(BaseSubsession):
    pass

class Player(BasePlayer):
    #otree likes currency fields for payoffs. If you want to change it to dollars instead of points
    #you need to go to settings and change use_points to "False"
    chosen_num = models.IntegerField(label="The income value selected is: ", min=1, max=6)
    charity_num = models.IntegerField(label="The charity value selected is: ", min=1, max=6)
    first_num = models.CurrencyField()
    second_num = models.CurrencyField()
    charity_pay = models.CurrencyField()
    charity = models.IntegerField()
    total_charity = models.CurrencyField()
    #This is all the PostSurvey questions. You can adjust the choices here, but if you want to change
    #the choices you need to change them here, in the PostSurvey page section and on the html page
    Age = models.IntegerField(label="Please choose your age range:", choices= [[1,'>18'], [2, '18-25'], [3, '25-35'], [4, '35-45'], [5, '45<'],])
    Gender = models.StringField(label= "Please choose your gender:", choices=['Male', 'Female', 'Prefer Not To Answer'])
    School = models.StringField(label="Please choose your highest level of education attained", choices=['Less than highschool', 'High School', 'Bachelor/Associates Degree', 'Masters', 'Phd', 'Prefer Not To Answer'])
    Work_actual = models.StringField(label="What is the highest level of employment you have reached?", choices=['Entry-level', 'Manager', 'Director', 'Vice-President', 'Chief Executive', 'Not Applicable'])
    Work_hypo = models.StringField(label="What is the highest level of employment you aspire to", choices=['Entry-level', 'Manager', 'Director', 'Vice-President', 'Chief Executive', 'Not Applicable'])

class Group(BaseGroup):
    dice_roll_1 = models.IntegerField()
    dice_roll_2 = models.IntegerField()
    match = BooleanField()

# Functions
#This needs to stay in the session portion so that the groups each get different rolls (but players within group get the same)
def creating_session(session):
    for groups in session.get_groups():
        groups.dice_roll_1 = random.randint(1, 6)
        #groups.die_roll_1 = random.choice(C.options)

    for groups in session.get_groups():
        groups.dice_roll_2 = random.randint(1, 6)
        #groups.die_roll_2 = random.choice(C.options)
        #Didn't test this, but it should work since its the same principal as the single player version I did test.
        #I'm just running out of time!

# PAGES
class Instructions(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

class RollOne(Page):
    timeout_seconds = 180
    form_model = 'player'
    form_fields = ['chosen_num']

    def vars_for_template(player: Player):
        group=player.group
        video_filename = f'Dice.{group.dice_roll_1}.mp4'
        return {
            'video_filename': video_filename,
        }

    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.chosen_num=6

class RollTwo(Page):
    timeout_seconds = 180
    form_model = 'player'
    form_fields = ['charity_num']

    def vars_for_template(player: Player):
        group=player.group
        video_filename2 = f'Dice.{group.dice_roll_2}.mp4'
        return {
            'video_filename2': video_filename2,
        }

    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.charity_num=6

class WaitPageP(WaitPage):
    pass

class WaitPageOne(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        players = group.get_players()
        p1_chosen_num = players[0].chosen_num
        p2_chosen_num = players[1].chosen_num
        p3_chosen_num = players[2].chosen_num
#For the groups you need to set a groupwide variable for each of the players choices before you can compare them.
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
#This just basically says if they match and are 6, or they don't match players get 0, otherwise they get what they chose
class WaitPageTwo(WaitPage):
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
                    p.second_num = 0
                    p.charity = 10
                else:
                    p.second_num = p.charity_num*2
                    p.charity = 10-(p.charity_num*2)
            else:
                p.second_num = 0
#This is the payoffs section
        for p in group.get_players():
            if p.round_number == 1:
                p.payoff = p.first_num + p.second_num + C.show_up
                p.total_charity = p.charity
            else:
                p.payoff = p.first_num + p.second_num
                previous_total = p.in_round(p.round_number-1).total_charity
                p.total_charity = previous_total + p.charity
#If you move charity first, you need to move this to the rev wait page

class Results(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS #this displays on the final round only

class PostSurvey(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS

    form_model = 'player'
    form_fields = ['Age', 'Gender', 'School', 'Work_actual', "Work_hypo"]
#if adding or removing a survey question change it here

#Revenue first
page_sequence = [Instructions, WaitPageP, RollOne, WaitPageOne, RollTwo, WaitPageTwo, Results, PostSurvey]

#Charity first
#page_sequence = [Instructions, WaitPageP, RollTwo, WaitPageTwo, RollOne, WaitPageOne, Results, PostSurvey]

#If you want to add the post experiment survey as a separate app (so all the survey info goes to that app)
#remove ", PostSurvey" from the page_sequence. You don't actually need to delete it