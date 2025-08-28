from otree.api import *
import itertools


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'DiceDiceBaby_group_fixed_one_roll'
    PLAYERS_PER_GROUP = 3 #none means no groups (each player plays individually)
    NUM_ROUNDS = 1 #This is where you change the number of rounds. If you have more than 1 round, you need to change the if statement on the roll page
    show_up = 0  #This would be show up fee, it's already set up to only add once

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    match = models.BooleanField()
    total_charity=models.IntegerField()
    treatment = models.IntegerField()

class Player(BasePlayer):
    treatment = models.IntegerField()
    rev_num = models.IntegerField(label="Please enter the revenue value", min=1, max=6)
    charity_num = models.IntegerField(label="Please enter the charity value", min=1, max=6)
    rev_earn = models.CurrencyField() #otree liked payouts to be in currency.
    charity_earn = models.CurrencyField()
    charity = models.IntegerField()
    total_charity = models.CurrencyField(initial=0)
    #This is all the PostSurvey questions. You can adjust the choices here, but if you want to change
    #the choices you need to change them here, in the PostSurvey page section and on the html page
    Age = models.IntegerField(label="Please choose your age range:", choices= [[1,'>18'], [2, '18-25'], [3, '25-35'], [4, '35-45'], [5, '45<'],])
    Gender = models.StringField(label= "Please choose your gender:", choices=['Male', 'Female', 'Prefer Not To Answer'])
    School = models.StringField(label="Please choose your highest level of education attained", choices=['Less than highschool', 'High School', 'Bachelor/Associates Degree', 'Masters', 'Phd', 'Prefer Not To Answer'])
    Work_actual = models.StringField(label="What is the highest level of employment you have reached?", choices=['Entry-level', 'Manager', 'Director', 'Vice-President', 'Chief Executive', 'Not Applicable'])
    Work_hypo = models.StringField(label="What is the highest level of employment you aspire to", choices=['Entry-level', 'Manager', 'Director', 'Vice-President', 'Chief Executive', 'Not Applicable'])



#functions
#This will divide the players into 4 groups. It can be changed easily, but needs to be changes here
#and new/changes if statements on the Roll page (use {{ elif }} / {{ end elif }}
# Can also add "and player.round_number == 1/2/3/etc" for  multiple rounds.
#Currently, I have it so players see 1, 2, 3, 4.
#If you want to show everyone the same number you can erase this part and use player.round_number == if you're doing multiple rounds.
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
        #this part keeps the same treatments for the groups in each round.
        #If you want them different then you can remove the whole if statement
        #if you're copying this to another app to make changes, you need to import itertools up top
        #This is only set up for one round. If you want multiple rounds you need to change the roll page


# PAGES
class Instructions(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

class Waiting(WaitPage):
    pass

class Roll(Page):
    timeout_seconds = 10 #This is how long to stay on the roll page before automatically moving forward
    #Just change this number if you want it up for longer or shorter

class RevPage(Page):
    form_model = 'player'
    form_fields = ['rev_num']

    timeout_seconds = 180 #How long the page stays up before it automatically moving forward. Can change it easilu

    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.rev_num = 6 #Sets it to the 0 payout if the timeout happens
            #Change this is the payout changes

class RevWait(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        players = group.get_players()
        p1_rev_num = players[0].rev_num
        p2_rev_num = players[1].rev_num
        p3_rev_num = players[2].rev_num
        #Apparenly you can't use the subscription [] in the if statement, so you need to make a specific variable for each players choice
        #Don't get rif of this without replacing it with something better

        if p1_rev_num == p2_rev_num and p2_rev_num == p3_rev_num:
            group.match = True
        else:
            group.match = False

        for p in players:
            if group.match == False:
                p.rev_earn = 0
            elif p.rev_num == 6:
                p.rev_earn = 0
            else:
                p.rev_earn = p.rev_num
                #This all sets the payoffs, you can change them around if you change payoffs,
                #but keep it in the order you want the program to look at it.
                #specific cases first then general


class CharityPage(Page):
    form_model = 'player'
    form_fields = ['charity_num']

    timeout_seconds = 180 #How long you want the page to be active for

    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.charity_num = 6 #whatever the 0 payoff number is

class CharityWait(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        players = group.get_players()
        p1_charity_num = players[0].charity_num #players star with 0, not 1
        p2_charity_num = players[1].charity_num
        p3_charity_num = players[2].charity_num
#Again, you need to make a variable from the specific player, you can't compare them without this step
        if p1_charity_num == p2_charity_num and p2_charity_num == p3_charity_num:
            group.match = True
        else:
            group.match = False


        for p in players:
            if group.match == False:
                p.charity_earn = 0
                p.charity = 10
            elif p.charity_num == 6:
                p.charity_earn = 0
                p.charity = 10
            else:
                p.charity_earn = p.charity_num*2
                p.charity = 10-(p.charity_num*2)

        for p in group.get_players():
            if p.round_number == 1:
                p.payoff = p.rev_earn + p.charity_earn + C.show_up
                p.total_charity = p.charity
            else:
                p.payoff = p.rev_earn + p.charity_earn
                previous_total = p.in_round(p.round_number-1).total_charity
                p.total_charity = previous_total + p.charity


class Results(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS
    #this only displays on the last round


class PostSurvey(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS

    form_model = 'player'
    form_fields = ['Age', 'Gender', 'School', 'Work_hypo', 'Work_actual']
    #if you change the demographic questions change them here. If you remove them to use a separate app, just remove them

#Revenue page first
page_sequence = [Instructions, Waiting, Roll, RevPage, RevWait, CharityPage, CharityWait, Results, PostSurvey]
#Charity page first
#page_sequence = [Instructions, Waiting, Roll, CharityPage, CharityWait, RevPage, RevWait, Results, PostSurvey]
#If you use this, you must also move the payoffs portion to the rev page wait page