from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound, App


class OSOneshotCatMouse(Quest):

    APP_NAME = 'org.gnome.Terminal'

    __quest_name__ = 'The Terminal - 1 - Cat and Mouse'
    __tags__ = ['mission:saniel', 'pathway:operating system', 'difficulty:hard']
    __mission_order__ = 250
    __pathway_order__ = 250

    TOTAL_MESSAGES = 18

    def setup(self):
        self._app = App(self.APP_NAME)
        return self.step_begin

    def step_begin(self):
        self.deploy_file('mouse', '~/yarnbasket/', override=True)
        # intro dialogue
        for index in range(1, 5):
            self.wait_confirm(str(index))
        # launch the terminal for the user, makes it easier - this is the first quest
        self._app.launch()
        self.wait_for_app_launch(self._app, pause_after_launch=2)

        return self.step_main_loop, 5

    def step_main_loop(self, message_index):
        if message_index > self.TOTAL_MESSAGES:
            return self.step_end
        elif message_index < 1:
            message_index = 1

        message_id = str(message_index)

        def _direction_choice(direction_choice_var):
            return direction_choice_var

        action = self.show_choices_message(message_id, ('BAK', _direction_choice, True),
                                           ('FWD', _direction_choice, False)).wait()
        go_back = action.future.result()

        if go_back:
            message_index -= 1
        else:
            message_index += 1

        return self.step_main_loop, message_index

    def step_end(self):
        self.wait_confirm('END')
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
