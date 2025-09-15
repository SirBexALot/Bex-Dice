from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'DiceDiceBaby_Demo_Survey'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    Age = models.IntegerField(label="Please choose your age range:", choices=[[1, '>18'], [2, '18-25'], [3, '25-35'], [4, '35-45'], [5, '45<'], ])
    Gender = models.StringField(label="Please choose your gender:", choices=['Male', 'Female', 'Prefer Not To Answer'])
    School = models.StringField(label="Please choose your highest level of education attained", choices=['Less than highschool', 'High School', 'Bachelor/Associates Degree', 'Masters', 'Phd', 'Prefer Not To Answer'])
    Work_actual = models.StringField(label="What is the highest level of employment you have reached?", choices=['Entry-level', 'Manager', 'Director', 'Vice-President', 'Chief Executive', 'Not Applicable'])
    Work_hypo = models.StringField(label="What is the highest level of employment you aspire to", choices=['Entry-level', 'Manager', 'Director', 'Vice-President', 'Chief Executive', 'Not Applicable'])

# PAGES
class Survey(Page):
    form_model = 'player'
    form_fields = ['Age', 'Gender', 'School', 'Work_actual', "Work_hypo"]


page_sequence = [Survey]
