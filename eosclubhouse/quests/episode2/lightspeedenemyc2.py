from eosclubhouse.apps import LightSpeed
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class LightSpeedEnemyC2(Quest):

    APP_NAME = 'com.endlessm.LightSpeed'

    def __init__(self):
        super().__init__('LightSpeedEnemyC2', 'riley')
        self._app = LightSpeed()

    def step_begin(self):
        if not self._app.is_running():
            self.show_hints_message('LAUNCH')
            self.give_app_icon(self.APP_NAME)
            self.wait_for_app_launch(self._app, pause_after_launch=2)

        self._app.set_level(8)
        self.show_hints_message('EXPLAIN')
        return self.step_wait_for_flip

    @Quest.with_app_launched(APP_NAME)
    def step_code(self):
        if (not self._app.get_js_property('flipped') and self._app.get_js_property('playing')) \
           or self.debug_skip():
            return self.step_play

        self.show_hints_message('CODE')

        self.wait_for_app_js_props_changed(self._app, ['flipped', 'playing'])
        return self.step_code

    @Quest.with_app_launched(APP_NAME)
    def step_play(self):
        self.show_hints_message('PLAYTEST')
        self.pause(10)

        min_y = self._app.get_js_property('obstacleType3MinY', +10000)
        max_y = self._app.get_js_property('obstacleType3MaxY', -10000)
        if min_y > max_y:
            self.show_hints_message('NOENEMIES')
            return self.step_wait_for_flip
        if min_y == max_y:
            self.show_hints_message('NOTMOVING')
            return self.step_wait_for_flip
        return self.step_success

    @Quest.with_app_launched(APP_NAME)
    def step_wait_for_flip(self):
        if not self._app.get_js_property('flipped') or self.debug_skip():
            self.wait_for_app_js_props_changed(self._app, ['flipped'])
        return self.step_code

    @Quest.with_app_launched(APP_NAME)
    def step_success(self):
        self.conf['complete'] = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.show_confirm_message('SUCCESS', confirm_label='Bye').wait()
        self.stop()
