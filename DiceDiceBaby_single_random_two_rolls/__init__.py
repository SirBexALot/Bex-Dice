from otree.api import *
import random

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'DiceDiceBaby_single_random_two_rolls'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 2
    show_up = 0 #This is if you want to have a show up payment
    #options = [1, 2, 3, 4, 5, 6] You can put any you want here for a limited random choice

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    roll_one = models.IntegerField()
    roll_two = models.IntegerField()
    rev_num = models.IntegerField(label = 'Please enter your revenue number', min = 1, max = 6)
    charity_num = models.IntegerField(label = 'Please enter your charity number', min = 1, max = 6)
    rev_earn = models.IntegerField()
    charity_earn = models.IntegerField()
    donation = models.IntegerField()
    total_donation = models.CurrencyField(initial = 0)
    # This is all the demographic questions for the Post experiment survey
    Age = models.IntegerField(label="Please choose your age range:", choices=[[1, '>18'], [2, '18-25'], [3, '25-35'], [4, '35-45'], [5, '45<'], ])
    Gender = models.StringField(label="Please choose your gender:", choices=['Male', 'Female', 'Prefer Not To Answer'])
    School = models.StringField(label="Please choose your highest level of education attained", choices=['Less than highschool', 'High School', 'Bachelor/Associates Degree', 'Masters', 'Phd', 'Prefer Not To Answer'])
    Work_actual = models.StringField(label="What is the highest level of employment you have reached?", choices=['Entry-level', 'Manager', 'Director', 'Vice-President', 'Chief Executive', 'Not Applicable'])
    Work_hypo = models.StringField(label="What is the highest level of employment you aspire to", choices=['Entry-level', 'Manager', 'Director', 'Vice-President', 'Chief Executive','Not Applicable'])


#FUNCTIONS
def creating_session(subsession):
    for p in subsession.get_players():
        p.roll_one = random.randint(1, 6)
        p.roll_two = random.randint(1, 6)
        #this creates the random dice roll using all integers between 1 and 6.
        #If you want to have a non-sequential set of numbers you need to put your options in the constants class
        #then you would replace the p.roll options with:
        #p.roll_one = random.choice(C.options)
        #p.roll_two = random.choice(C.options)
        #I haven't tested this because I only just realized I should have included this option while testing these on the lasy day
        #fairly confident in it though, since all it's changing is a randint to a random choice

# PAGES
class Instructions(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1
    #this makes the instructions only display in round 1

class Waiting(WaitPage):
    pass

class RevPage(Page):
    timeout_seconds = 60 #You can change how long people can see each page here. Just change it in the instructions too

    def vars_for_template(player):
        video_filename= f'Dice.{player.roll_one}.mp4'
        return{
            'video_filename': video_filename
        }
#Don't touch this part. It lets the random number choose the file.
    # If you replace the videos (likely) just rename them the same way and it will keep working

    form_model = 'player'
    form_fields = ['rev_num']
    #If you want anything else added here, put it in the form fields section

    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.rev_num = 6
    #Since 6 is 0, timeouts pay 0. Change it if you change the payoff structure

class RevWait(WaitPage):
    @staticmethod
    def after_all_players_arrive(group):
        for p in group.get_players():
            if p.rev_num == 6:
                p.rev_earn = 0
            else:
                p.rev_earn = p.rev_num
        #If you change it charity first, you need to move the payoffs section to here

class CharityPage(Page):
    timeout_seconds = 60

    def vars_for_template(player):
        video_filename= f'Dice.{player.roll_two}.mp4'
        return{
            'video_filename': video_filename
        }

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
#This is your payoffs code
        for p in players:
            if p.round_number == 1:
                p.payoff = C.show_up + p.charity_earn + p.rev_earn
                p.total_donation = p.donation
            else:
                p.payoff = p.charity_earn + p.rev_earn
                previous_donation = p.in_round(p.round_number-1).total_donation
                p.total_donation = previous_donation + p.donation
#If you move to charity first, you need to move this section to the RevWait page.

class Results(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS
    #Just displays in whatever the last round is

class PostSurvey(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS

    form_model = 'player'
    form_fields = ['Age', 'Gender', 'School', 'Work_actual', "Work_hypo"]
    #If you change the survey questions, change it here and on the PostSurvey page.
    #If you use the survey as a separate app, you can erase it from the page sequence

#Rev first
page_sequence = [Instructions, Waiting, RevPage, RevWait, CharityPage, CharityWait, Results, PostSurvey]
#charity first
#page_sequence = [Instructions, Waiting, CharityPage, CharityWait, RevPage, RevWait, Results, PostSurvey]

