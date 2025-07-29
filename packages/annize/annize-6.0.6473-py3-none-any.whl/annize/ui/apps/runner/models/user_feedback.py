# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve.driver

import annize.i18n
import annize.user_feedback


class UserFeedback(klovve.model.Model):

    annize_application: klovve.app.Application = klovve.model.property()

    feedback_tuples: list[tuple[int, klovve.views.interact.AbstractInteract]] = klovve.model.list_property()

    class __(klovve.model.ListTransformer):
        def output_item(self, item):
            return item[1]
    feedback_items: list[klovve.ui.View] = klovve.model.transformed_list_property(__(),
                                                                                  input_list_property=feedback_tuples)

    def _(self):
        return _UserFeedbackController(self)
    feedback_controller: "_UserFeedbackController" = klovve.model.computed_property(_)

    def handle_answered(self, interact: klovve.views.interact.AbstractInteract, answer: object) -> None:
        for i_tuple, (feedback_reqid, feedback_interact) in enumerate(self.feedback_tuples):
            if feedback_interact == interact:
                self.feedback_controller.set_answer(feedback_reqid, answer)
                self.feedback_tuples.pop(i_tuple)
                break


class _UserFeedbackController(annize.user_feedback.UserFeedbackController):

    def __init__(self, user_feedback: UserFeedback):  # TODO scrollview for message?!
        self.__user_feedback = user_feedback
        self.__nextid = 0
        self.__requests = []  # TODO multithreading  TODO cleanup
        self.__answers = {}  # TODO multithreading  TODO cleanup

    def __get_answer(self, reqid):
        while reqid not in self.__answers:
            pass
        return self.__answers.pop(reqid)

    def set_answer(self, reqid, answer):
        self.__answers[reqid] = answer

    def __manageui(self):  # TODO nicer
        return # TODO
        if self.__window.userfeedbackrevealer.props.reveal_child:
            self.__window.successstack.set_visible_child_full("user_feedback", Gtk.StackTransitionType.CROSSFADE)
        else:
            self.__window.successstack.set_visible_child_full("spinner", Gtk.StackTransitionType.CROSSFADE)

    def message_dialog(self, message, answers, config_key):  # TODO noh config_key
        reqid, self.__nextid = self.__nextid, self.__nextid + 1
        async def _():
            self.__message_dialog(reqid, message, answers, config_key)
        klovve.driver.Driver.get().loop.enqueue(_())
        return self.__get_answer(reqid)

    def __message_dialog(self, reqid, message, answers, config_key):
        feedback_item = klovve.views.interact.Message(message=message, choices=[(s, i) for i, s in enumerate(answers)])
        self.__user_feedback.feedback_tuples.append((reqid, feedback_item))
        # TODO config_key
        if False: annize.i18n.tr("an_Userfeedback_AnswerAutomatableByKey")

    def input_dialog(self, question, suggested_answer, config_key):
        reqid, self.__nextid = self.__nextid, self.__nextid + 1
        async def _():
            self.__input_dialog(reqid, question, suggested_answer, config_key)
        klovve.driver.Driver.get().loop.enqueue(_())
        return self.__get_answer(reqid)

    def __input_dialog(self, reqid, question, suggested_answer, config_key):
        feedback_item = klovve.views.interact.TextInput(message=question, suggestion=suggested_answer)
        self.__user_feedback.feedback_tuples.append((reqid, feedback_item))
        # TODO config_key
        if False: annize.i18n.tr("an_Userfeedback_AnswerAutomatableByKey")

    def choice_dialog(self, question, choices, config_key):
        pass  # TODO
