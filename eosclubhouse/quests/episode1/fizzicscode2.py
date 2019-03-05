from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App, Sound


class FizzicsCode2(Quest):

    APP_NAME = 'com.endlessm.Fizzics'

    def __init__(self):
        super().__init__('Fizzics Code 2', 'riley')
        self._app = App(self.APP_NAME)
        self.gss.connect('changed', self.update_availability)
        self.available = False
        self.update_availability()

    def update_availability(self, gss=None):
        if self.conf['complete']:
            self.set_next_episode('episode2')
            return
        if self.is_named_quest_complete("FizzicsCode1"):
            self.available = True

    def step_begin(self):
        if not self._app.is_running():
            self.show_hints_message('LAUNCH')
            Desktop.focus_app(self.APP_NAME)
            self.wait_for_app_launch(self._app)
            self.pause(2)

        return self.step_flip

    @Quest.with_app_launched(APP_NAME)
    def step_flip(self):
        if self._app.get_js_property('flipped'):
            return self.step_explanation

        Sound.play('quests/step-forward')
        self.show_hints_message('FLIP')
        while not self._app.get_js_property('flipped') and not self.is_cancelled():
            self.wait_for_app_js_props_changed(self._app, ['flipped'])

        return self.step_explanation

    @Quest.with_app_launched(APP_NAME)
    def step_explanation(self):
        if self._app.get_js_property('gravity_0', 0) < 0:
            return self.step_end

        Sound.play('quests/step-forward')
        self.show_hints_message('EXPLANATION')
        while not self._app.get_js_property('gravity_0', 0) < 0 and not self.is_cancelled():
            # @todo: Connect to app property changes instead of
            # polling. This needs a fix in Clippy. See
            # https://phabricator.endlessm.com/T25359
            self.pause(0.5)

        return self.step_end

    def step_end(self):
        Sound.play('quests/step-forward')
        self.conf['complete'] = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.show_message('END', choices=[('Bye', self.stop())])
