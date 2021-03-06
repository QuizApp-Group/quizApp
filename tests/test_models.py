"""Run tests on the database models.
"""
from __future__ import unicode_literals
import os
from datetime import datetime, timedelta

import pytest
from sqlalchemy import inspect
import mock

from tests.factories import ExperimentFactory, \
    ChoiceFactory, QuestionFactory, ScorecardFactory
from quizApp import models


def test_db_rollback1():
    """Along with test_db_rollback2, ensure rollbacks are working correctly.
    """
    exp = models.Role(name="notaname-1")
    exp.save()
    assert models.Role.query.filter_by(name="notaname-1").count() == 1
    assert models.Role.query.filter_by(name="notaname-2").count() == 0


def test_db_rollback2():
    """Along with test_db_rollback1, ensure rollbacks are working correctly.
    """
    exp = models.Role(name="notaname-2")
    exp.save()
    assert models.Role.query.filter_by(name="notaname-1").count() == 0
    assert models.Role.query.filter_by(name="notaname-2").count() == 1


def test_experiment_running():
    experiment = models.Experiment(
        start=datetime.now() + timedelta(days=-100),
        stop=datetime.now() + timedelta(days=100)
    )

    assert experiment.running

    experiment.start = datetime.now() + timedelta(days=100)

    assert not experiment.running

    experiment.start = datetime.now() + timedelta(days=-200)
    experiment.stop = datetime.now() + timedelta(days=-100)

    assert not experiment.running


def test_assignment_validators():
    """Test validators of the Assignment model.
    """
    assn = models.Assignment()
    exp = ExperimentFactory()
    activity = models.Activity()
    assn.experiment = exp
    activity.num_media_items = -1

    choice = ChoiceFactory()
    question = models.Question()
    question.num_media_items = -1

    assn.activity = question
    result = models.MultipleChoiceQuestionResult()
    result.choice = choice

    with pytest.raises(AssertionError):
        assn.result = result

    question.choices.append(choice)

    assn.result = result

    # Test the media item number validations
    question2 = QuestionFactory()
    question2.num_media_items == len(assn.media_items) + 1

    with pytest.raises(AssertionError):
        assn.activity = question2

    question2.num_media_items = -1
    assn.activity = question2

    question2.num_media_items = len(assn.media_items)
    assn.activity = question2


def test_result_validators():
    """Test for various result validators.
    """
    # Make sure types are correct
    choice = ChoiceFactory()
    mc_question = models.MultipleChoiceQuestion(num_media_items=-1)
    mc_result = models.MultipleChoiceQuestionResult(choice=choice)
    fa_question = models.FreeAnswerQuestion(num_media_items=-1)
    fa_result = models.FreeAnswerQuestionResult()
    assignment = models.Assignment()

    experiment = ExperimentFactory()
    assignment.experiment = experiment

    assignment.activity = mc_question

    with pytest.raises(AssertionError):
        assignment.result = mc_result

    mc_question.choices.append(choice)
    assignment.result = mc_result

    assignment = models.Assignment()
    assignment.experiment = experiment
    assignment.activity = mc_question

    with pytest.raises(AssertionError):
        assignment.result = fa_result

    assignment = models.Assignment()
    assignment.experiment = experiment
    assignment.activity = fa_question

    with pytest.raises(AssertionError):
        assignment.result = mc_result


def test_graph_filename():
    """Make sure graph filenames work correctly.
    """
    path = "/foo/bar/baz/"
    filename = "boo.png"

    full_path = os.path.join(path, filename)

    graph = models.Graph(path=full_path, name="Foobar")

    assert graph.filename() == filename


def test_graph_directory():
    path = "/foo/bar/baz"
    filename = "boo.png"

    full_path = os.path.join(path, filename)
    graph = models.Graph(path=full_path, name="Foobar")

    assert graph.directory == path


def test_save():
    """Make sure saving works correctly.
    """
    role = models.Role(name="Foo")

    role.save()

    inspection = inspect(role)

    assert not inspection.pending

    role2 = models.Role(name="bar")

    role2.save(commit=False)

    inspection = inspect(role2)

    assert inspection.pending


def test_activity_get_score():
    activity = models.Activity()
    result = models.Result()
    assert None is activity.get_score(result)


def test_free_answer_question_get_score():
    fa_question = models.FreeAnswerQuestion()
    fa_result = models.FreeAnswerQuestionResult()

    assert fa_question.get_score(fa_result) == 0

    fa_result.text = "AAAA"

    assert fa_question.get_score(fa_result) == 1
    assert fa_question.get_score(None) == 0


def test_assignment_get_score():
    assignment = models.Assignment()

    with pytest.raises(AttributeError):
        assert assignment.get_score() is None


def test_integer_question_validators():
    int_question = models.IntegerQuestion()
    int_result = models.IntegerQuestionResult()

    int_question.lower_bound = 1

    with pytest.raises(AssertionError):
        int_question.answer = 0

    int_question.answer = 1
    int_question.upper_bound = 2

    with pytest.raises(AssertionError):
        int_question.answer = 3

    int_question.answer = 2

    int_result.integer = 2

    assert int_question.get_score(int_result) == 1

    int_result.integer = 1

    assert int_question.get_score(int_result) == 0


def test_activity_correct():
    activity = models.Activity()
    activity.is_correct(None)


def test_activity_str():
    activity = models.Activity()

    with pytest.raises(NotImplementedError):
        str(activity)


def test_question_str():
    question = QuestionFactory()

    assert question.question in str(question)


def test_scorecard_str():
    scorecard = ScorecardFactory()

    assert scorecard.title in str(scorecard)


def test_assignment_correct():
    assignment = models.Assignment()
    result = models.Result()
    activity = mock.MagicMock(autospec=models.Activity())
    activity.Meta.result_class = models.Result
    activity.num_media_items = -1
    assignment.activity = activity
    assignment.result = result

    assignment.correct()

    activity.is_correct.assert_called_once_with(result)


def test_integer_question_correct():
    int_question = models.IntegerQuestion()
    int_result = models.IntegerQuestionResult()
    int_question.answer = 5

    assert not int_question.is_correct(None)
    assert not int_question.is_correct(int_result)

    int_result.integer = 5

    assert int_question.is_correct(int_result)


def test_mc_question_correct():
    mc_question = models.MultipleChoiceQuestion()
    correct_choice = models.Choice(correct=True)
    incorrect_choice = models.Choice(correct=False)
    mc_result = models.MultipleChoiceQuestionResult
    mc_question.choices = [correct_choice, incorrect_choice]

    mc_result.choice = incorrect_choice

    assert not mc_question.is_correct(None)
    assert not mc_question.is_correct(mc_result)

    mc_result.choice = correct_choice

    assert mc_question.is_correct(mc_result)


def test_free_answer_question_is_correct():
    fa_question = models.FreeAnswerQuestion()
    fa_result = models.FreeAnswerQuestionResult()

    assert not fa_question.is_correct(fa_result)
    assert not fa_question.is_correct(None)

    fa_result.text = "aaaa"

    assert fa_question.is_correct(fa_result)


def test_scorecard_correct():
    scorecard = models.Scorecard()

    assert scorecard.is_correct(None)


def test_multiselect_question_result():
    question = models.MultiSelectQuestion()
    result = models.MultiSelectQuestionResult()
    choice1 = ChoiceFactory()
    choice2 = ChoiceFactory()
    choice3 = ChoiceFactory()
    question.choices = [choice1, choice2]
    question.num_media_items = -1

    result.choices = [choice3]
    assignment = models.Assignment()
    assignment.activity = question

    with pytest.raises(AssertionError):
        assignment.result = result

    result.choices = [choice1, choice2]

    assignment.result = result

    assert choice1.choice in str(result)
    assert choice2.choice in str(result)


def test_singleselect_question_result():
    result = models.MultipleChoiceQuestionResult()
    choice = ChoiceFactory()

    result.choice = choice

    assert choice.choice in str(result)


def test_result():
    result = models.Result()

    with pytest.raises(NotImplementedError):
        str(result)


def test_freeanswer_question_result():
    result = models.FreeAnswerQuestionResult()
    result.text = "jiefdjsae"

    assert result.text in str(result)


def test_scorecard_result():
    result = models.ScorecardResult()
    str(result)


def test_integer_answer_question_result():
    result = models.IntegerQuestionResult()
    result.integer = 5993

    assert str(result.integer) in str(result)


def test_choice_str():
    choice = ChoiceFactory()

    assert choice.label in str(choice)
    assert choice.choice in str(choice)

    label = choice.label
    choice.label = ""

    assert choice.choice == str(choice)

    choice.label = label
    choice.choice = ""

    assert choice.label == str(choice)
