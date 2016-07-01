#!/bin/env python2

"""Using excel files, populate the database with some placeholder data.
"""

from quizApp.models import Question, Answer, Result, Student, StudentTest, \
        Graph, Experiment, User
from quizApp import db
from quizApp.models import *
from sqlalchemy import and_
import pandas as pd
from datetime import datetime, timedelta
import os
from sqlalchemy.orm.exc import NoResultFound
import pdb

SQLALCHEMY_ECHO = False
db.drop_all()
db.create_all()

question_type_mapping = {"multiple_choice": "question_mc_singleselect",
                         "heuristic": "question_mc_singleselect_scale",
                         "rating": "question_mc_singleselect_scale",
                         "pre_test": "question"}

pre_test = Experiment(name="pre_test",
                      start=datetime.now(),
                      stop=datetime.now() + timedelta(days=3))

test = Experiment(name="test",
                  start=datetime.now(),
                  stop=datetime.now() + timedelta(days=5))

post_test = Experiment(name="post_test",
                       start=datetime.now() + timedelta(days=-3),
                       stop=datetime.now())

experiments = {"pre_test": pre_test,
               "test": test,
               "post_test": post_test}

db.session.add(pre_test)
db.session.add(test)
db.session.add(post_test)

DATA_ROOT = "quizApp/data/"

questions = pd.read_excel(os.path.join(DATA_ROOT,
                                       'DatasetsAndQuestions.xlsx'),
                          'Questions')

for _, data in questions.iterrows():
    # Convert from 0 indexed to 1 indexed
    dataset_id = data.dataset_id + 1
    dataset = Dataset.query.get(dataset_id)

    if not dataset:
        dataset = Dataset(id=dataset_id)
        db.session.add(dataset)

    question = Question(
        id=data.question_id,
        datasets=[dataset],
        question=data.question_text,
        type=question_type_mapping[data.question_type])

    if "scale" in question.type:
        for i in range(0, 5):
            question.choices.append(Choice(choice=str(i), label=str(i),
                                           correct=True))

    db.session.add(question)

choices = pd.read_excel(os.path.join(DATA_ROOT, 'DatasetsAndQuestions.xlsx'),
                        'Answers')
for _, data in choices.iterrows():
    choice = Choice(
        #id=data.answer_id,
        question_id=data.question_id,
        choice=data.answer_text,
        correct=data.correct == "yes",
        label=data.answer_letter)
    db.session.add(choice)

df_graphs = pd.read_excel(os.path.join(DATA_ROOT, 'graph_table.xlsx'),
                          'Sheet1')

for _, data in df_graphs.iterrows():
    graph = Graph(
        id=data.graph_id,
        dataset_id=data.dataset+1,
        filename=data.graph_location)
    db.session.add(graph)


# In this list, each list is associated with a participant (one to one).  The
# first three tuples in each list are associated with training questions.  The
# last three tuples in each list are associated with pre/post questions.  In
# each tuple, the first number represents the dataset of the question.  The
# second number is associated with the ID of the graph. TODO: simplify this
# relationship.  The order of the tuples along with the participant id gives
# the participant test id.  Note: No participant has two tuples with the same
# dataset - this means the relationship between participant test and dataset is
# many to one.

participant_question_list = \
[[(1, 2), (3, 2), (4, 0), (2, 1), (5, 0), (0, 0)],
 [(1, 2), (0, 2), (5, 1), (2, 0), (3, 0), (4, 1)],
 [(3, 0), (2, 1), (4, 0), (5, 1), (0, 0), (1, 2)],
 [(5, 2), (2, 2), (0, 1), (1, 0), (3, 1), (4, 0)],
 [(2, 2), (0, 1), (3, 1), (4, 0), (1, 1), (5, 1)],
 [(0, 0), (3, 0), (1, 0), (2, 2), (5, 2), (4, 2)],
 [(4, 2), (1, 1), (5, 2), (0, 0), (3, 1), (2, 1)],
 [(4, 2), (3, 0), (1, 2), (0, 1), (5, 2), (2, 1)],
 [(3, 1), (2, 0), (4, 2), (1, 1), (0, 1), (5, 2)],
 [(0, 2), (4, 1), (3, 0), (5, 0), (1, 1), (2, 0)],
 [(5, 1), (4, 1), (0, 2), (3, 2), (1, 2), (2, 0)],
 [(2, 1), (5, 0), (0, 2), (3, 2), (4, 2), (1, 1)],
 [(3, 1), (5, 2), (4, 1), (0, 2), (2, 0), (1, 0)],
 [(1, 1), (5, 1), (2, 2), (4, 0), (3, 1), (0, 2)],
 [(2, 0), (1, 0), (5, 0), (4, 1), (0, 2), (3, 2)],
 [(1, 1), (5, 1), (0, 2), (4, 2), (2, 1), (3, 1)],
 [(5, 1), (4, 2), (2, 0), (1, 2), (3, 2), (0, 1)],
 [(0, 0), (2, 2), (1, 0), (4, 1), (5, 2), (3, 2)],
 [(0, 1), (1, 2), (5, 2), (2, 0), (4, 2), (3, 0)],
 [(1, 0), (3, 2), (0, 0), (2, 2), (4, 0), (5, 0)],
 [(3, 2), (2, 1), (4, 1), (1, 0), (5, 1), (0, 0)],
 [(1, 0), (3, 2), (5, 0), (0, 1), (4, 1), (2, 2)],
 [(5, 2), (3, 1), (1, 1), (0, 0), (4, 0), (2, 2)],
 [(4, 1), (0, 0), (3, 1), (2, 1), (5, 1), (1, 0)],
 [(5, 0), (2, 0), (0, 1), (3, 0), (1, 1), (4, 2)],
 [(0, 2), (4, 0), (1, 1), (3, 1), (2, 2), (5, 0)],
 [(2, 0), (0, 0), (3, 0), (1, 2), (5, 0), (4, 1)],
 [(0, 1), (4, 2), (2, 1), (5, 2), (1, 0), (3, 0)],
 [(5, 0), (4, 0), (2, 2), (3, 0), (1, 2), (0, 1)],
 [(4, 0), (1, 2), (2, 1), (5, 1), (0, 2), (3, 2)]]

#temp created participant id list
# question_participant_id_list = [x + 1 for x in range(30)]
# heuristic_participant_id_list = [x + 1 for x in range(30,60)]

#read in participant lists
df_sid = pd.read_csv(os.path.join(DATA_ROOT, 'participant_id_list.csv'))
df_sid.Questions = df_sid.Questions.apply(lambda x: int(x))
df_sid.Heuristics = df_sid.Heuristics.apply(lambda x: int(x))
question_participant_id_list = [int(x) for x in list(df_sid.Questions)]
heuristic_participant_id_list = [int(x) for x in list(df_sid.Heuristics)]
combined_id_list = question_participant_id_list + heuristic_participant_id_list

for pid in combined_id_list:
    participant = Participant(
        id=pid,
        opt_in=False,
        progress="pre_test"
    )
    for exp in experiments.values():
        part_exp = ParticipantExperiment(
            progress=0,
            participant_id=pid,
            experiment_id=exp.id)
        db.session.add(part_exp)
    db.session.add(participant)

db.session.commit()

def create_participant_data(pid_list, participant_question_list, test, group):
    """
    sid_list: list of participant id's
    participant_question_list: magic list of lists of tuples
    test: pre_test or training or post_test
    group: question or heuristic
    """
    missing_qs = set()
    if test == 'pre_test' or test == 'post_test':
        question_list = [x[:3] for x in participant_question_list]
    else:
        #pick last three
        question_list = [x[3:] for x in participant_question_list]
    for n, participant in enumerate(question_list):
        #n is the nth participant
        participant_id = pid_list[n]
        participant_experiment = ParticipantExperiment.query.\
                filter_by(participant_id=participant_id).\
                filter_by(experiment_id=experiments[test].id).one()
        #count the order for each participant per test
        order = 0
        for ix, graph in enumerate(participant):
            participant_test_id = int(str(participant_id)+str(ix))
            dataset = graph[0]
            graph_id = int(str(dataset)+str(graph[1]+1))
            if test == 'pre_test' or test == 'post_test':
                order += 1
                #TODO: why +5
                question_id = int(str(dataset)+str(5))

                if not Question.query.get(question_id):
                    missing_qs.add(question_id)
                    continue

                #write row to db
                assignment = Assignment(
                    participant_id=participant_id,
                    activity_id=question_id,
                    experiment_id=experiments[test].id,
                    participant_experiment_id=participant_experiment.id,
                    graphs=[Graph.query.get(graph_id)])

                db.session.add(assignment)

            else: #training
                if group == 'heuristic':
                    #three questions per dataset, three datasets, so 9 questions
                    # for the training part
                    for x in range(6, 9):
                        order += 1
                        question_id = int(str(dataset)+str(x))

                        if not Question.query.get(question_id):
                            missing_qs.add(question_id)
                            continue

                        #write row to db
                        assignment = Assignment(
                            participant_id=participant_id,
                            activity_id=question_id,
                            experiment_id=experiments[test].id,
                            participant_experiment_id=participant_experiment.id,
                            graphs=[Graph.query.get(graph_id)])

                        db.session.add(assignment)
                else:
                    #multiple choice questions
                    for x in range(3):
                        order += 1
                        question_id = int(str(dataset)+str(x + 1))
                        #write row to db
                        if not Question.query.get(question_id):
                            missing_qs.add(question_id)
                            continue
                        assignment = Assignment(
                            participant_id=participant_id,
                            activity_id=question_id,
                            experiment_id=experiments[test].id,
                            participant_experiment_id=participant_experiment.id,
                            graphs=[Graph.query.get(graph_id)])

                        db.session.add(assignment)

                #only have rating question for training
                order += 1
                question_id = int(str(dataset)+str(4))
                #write row to db
                if not Question.query.get(question_id):
                    missing_qs.add(question_id)
                    continue

                assignment = Assignment(
                    participant_id=participant_id,
                    activity_id=question_id,
                    experiment_id=experiments[test].id,
                    participant_experiment_id=participant_experiment.id,
                    graphs=[Graph.query.get(graph_id)])

                db.session.add(assignment)

    db.session.commit()
    print "Completed storing {} {} tests".format(test, group)
    if missing_qs:
        print "Failed to find the following questions:"
        print missing_qs

#create all the participant_test table data
for test in ['pre_test', 'test', 'post_test']:
    create_participant_data(question_participant_id_list,
                            participant_question_list, test, 'question')
    create_participant_data(heuristic_participant_id_list,
                            participant_question_list, test, 'heuristic')
