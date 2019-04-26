import itertools

from eosclubhouse.libquest import Registry, Quest, QuestSet
from eosclubhouse.utils import QS, QuestStringCatalog
from clubhouseunittest import ClubhouseTestCase, test_all_episodes
from unittest import mock


class PhonyQuest(Quest):

    def __init__(self, quest_set):
        super().__init__('PhonyQuest for {}'.format(quest_set), quest_set.get_character())
        self.available = True

    def step_begin(self):
        print('Nothing to see here')


class TestQuestSets(ClubhouseTestCase):

    def setUp(self):
        self.reset_gss()
        Registry.load_current_episode()

    def _get_first_active_quest_set(self, quest_sets, exclude_quest_set):
        for quest_set in quest_sets:
            if quest_set is exclude_quest_set:
                continue
            if quest_set.active:
                return quest_set
        return None

    @test_all_episodes
    def test_empty_message_with_inactive_questsets(self):
        """Tests the QuestSets empty messages when other QuestSets are inactive."""
        quest_sets = Registry.get_quest_sets()
        for quest_set in quest_sets:
            self.deactivate_quest_set(quest_set)

        for quest_set in quest_sets:
            message = quest_set.get_empty_message()

            noquest_msg_id = '{}_NOTHING'.format(quest_set.get_character()).upper()

            expected_message = QS('NOQUEST_{}_{}'.format(Registry.get_loaded_episode_name(),
                                                         noquest_msg_id))
            if expected_message is None:
                expected_message = QS('NOQUEST_' + noquest_msg_id)

            self.assertEqual(message, expected_message)

    def test_episode_empty_message(self):
        """Tests whether a QuestSet correctly uses the episode's specific NOQUEST messages
        when available.
        """

        class PhonyAlice(QuestSet):
            __character_id__ = 'Alice'

        class PhonyBob(QuestSet):
            __character_id__ = 'Bob'

            def is_active(self):
                return True

        alice = PhonyAlice()
        bob = PhonyBob()

        Registry.get_loaded_episode_name = mock.Mock(return_value='phonyep')
        Registry.get_quest_sets = mock.Mock(return_value=[alice])

        string_catalog = QuestStringCatalog._csv_dict
        QuestStringCatalog.set_key_value_from_csv_row(('NOQUEST_ALICE_NOTHING',
                                                       'no quest', alice.get_character(),
                                                       'talk', '', ''),
                                                      string_catalog)

        QuestStringCatalog.set_key_value_from_csv_row(('NOQUEST_ALICE_BOB',
                                                       'no quest, check bob', alice.get_character(),
                                                       'talk', '', ''),
                                                      string_catalog)

        # We get any message
        noquest_info = string_catalog['NOQUEST_ALICE_NOTHING']
        ep_noquest_info = noquest_info.copy()
        ep_noquest_info['txt'] = 'ep_noquest_hello'

        noquest_alice_bob_info = string_catalog['NOQUEST_ALICE_BOB']
        ep_noquest_alice_bob_info = noquest_alice_bob_info.copy()
        ep_noquest_alice_bob_info['txt'] = 'check_bob'

        string_catalog.update({'NOQUEST_PHONYEP_ALICE_NOTHING': ep_noquest_info,
                               'NOQUEST_PHONYEP_ALICE_BOB': ep_noquest_alice_bob_info})

        # There's an episode specific noquest message and no other quest-set active.
        self.assertEqual(alice.get_empty_message(), ep_noquest_info['txt'])

        # There's no episode specific noquest message and no other quest-set active.
        del string_catalog['NOQUEST_PHONYEP_ALICE_NOTHING']
        self.assertEqual(alice.get_empty_message(), noquest_info['txt'])

        # There's an episode specific noquest message and an other quest-set active.
        Registry.get_quest_sets = mock.Mock(return_value=[alice, bob])
        self.assertEqual(alice.get_empty_message(), ep_noquest_alice_bob_info['txt'])

        # There's no episode specific noquest message and an other quest-set active.
        del string_catalog['NOQUEST_PHONYEP_ALICE_BOB']
        self.assertEqual(alice.get_empty_message(), noquest_alice_bob_info['txt'])

    @test_all_episodes
    def test_empty_message_with_active_questsets(self):
        """Tests the QuestSets empty messages when other QuestSet objects are active."""
        quest_sets = Registry.get_quest_sets()
        quest_sets_to_test = []

        for quest_set in quest_sets:
            # Skip checking the Trap quest set here as it's different.
            if str(quest_set) == 'TrapQuestSet':
                continue

            self.deactivate_quest_set(quest_set)
            quest_sets_to_test.append(quest_set)

        for quest_set in quest_sets_to_test:
            self.check_empty_message_with_active_questsets(quest_sets_to_test, quest_set)

    @test_all_episodes
    def test_can_complete_episode(self):
        """Tests there is at least one Quest in the QuestSets that complete the episode."""
        quest_sets = Registry.get_quest_sets()

        all_quests = itertools.chain.from_iterable((quest_set.get_quests()
                                                    for quest_set in quest_sets))
        has_quest_with_complete = any(quest.__complete_episode__ for quest in all_quests)
        self.assertTrue(has_quest_with_complete,
                        "Episode " + Registry.get_loaded_episode_name() +
                        " doesn't have any quest with __complete_episode__ = True.")

    def activate_quest_set(self, quest_set):
        quest_set.get_quests().insert(0, PhonyQuest(quest_set))
        quest_set.visible = True

    def deactivate_quest_set(self, quest_set):
        quests = quest_set.get_quests()
        if quests:
            if isinstance(quests[0], PhonyQuest):
                del quests[0]

        quest_set.visible = False

    def check_empty_message_with_active_questsets(self, quest_sets, test_quest_set):
        # Activate one quest set at a time and verify that the NOQUEST message matches the one
        # for quest set.
        for quest_set in quest_sets:
            if quest_set is test_quest_set:
                continue

            self.activate_quest_set(quest_set)

            empty_message = test_quest_set.get_empty_message()

            self.deactivate_quest_set(quest_set)

            noquest_msg_id = 'NOQUEST_{}_{}'.format(test_quest_set.get_character(),
                                                    quest_set.get_character())

            message = QS(noquest_msg_id.upper())

            quest_set.active = False

            self.assertEqual(empty_message, message,
                             'Failed while checking empty message from {} for '
                             'active {}'.format(test_quest_set, quest_set))