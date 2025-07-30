# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
#TODO weg?!?!
import typing as t

import annize.i18n
import annize.user_feedback


class TtyUserFeedbackController(annize.user_feedback.UserFeedbackController):

    def __dialog_frame_message(self, message: str) -> str:
        return f"--------------------------------------------------------------------------------\n{message}\n"

    def __dialog_frame_configkey(self, config_key: str) -> str:
        if config_key:
            return "\n" + annize.i18n.tr("an_Userfeedback_AnswerAutomatableByKey").format(**locals()) + "\n"
        return ""

    def __dialog_frame_actions(self, text: str) -> str:
        return f"--------------------------------------------------------------------------------\n{text}"

    def __action_line(self, num: t.Any, text: str) -> str:
        return f"{str(num).rjust(5, ' ')} : {text}\n"

    def __dialog(self, message: str, config_key: str, actionstext: str) -> str:
        if False:  # TODO check terminal available
            raise annize.user_feedback.UnsatisfiableUserFeedbackAttemptError()
        print(self.__dialog_frame_message(message)
              + self.__dialog_frame_configkey(config_key)
              + self.__dialog_frame_actions(actionstext))
        return input(">>> ")

    def message_dialog(self, message, answers, config_key):
        actionstext = annize.i18n.tr("an_Userfeedback_Tty_EnterAnswerNumber") + "\n\n"
        for ianswer, answer in enumerate(answers):
            actionstext += self.__action_line(ianswer, answer)
        while True:
            answer = self.__dialog(message, config_key, actionstext)
            try:
                answer = int(answer)
            except ValueError:
                continue
            if 0 <= answer < len(answers):
                return answer

    def input_dialog(self, question, suggested_answer, config_key):
        actionstext = annize.i18n.tr("an_Userfeedback_Tty_EnterAnswer") + "\n" \
                      + annize.i18n.tr("an_Userfeedback_Tty_EnterAnswerAlt").format(**locals()) + "\n\n"
        answer = self.__dialog(question, config_key, actionstext)
        if answer == "---":
            return None
        if answer == "!!!":
            return suggested_answer
        return answer

    def choice_dialog(self, question, choices, config_key):
        actionstext = annize.i18n.tr("an_Userfeedback_Tty_EnterAnswerChoiceNumber") + "\n\n"
        for ianswer, answer in enumerate(choices):
            actionstext += self.__action_line(ianswer, answer)
        actionstext += self.__action_line(-1, "Cancel")
        while True:
            answer = self.__dialog(question, config_key, actionstext)
            try:
                answer = int(answer)
            except ValueError:
                continue
            if answer == -1:
                return None
            if 0 <= answer < len(choices):
                return answer
