from aiogram.fsm.state import State, StatesGroup


class Survey(StatesGroup):
    name = State(); age = State(); sex = State(); height = State(); weight = State()
    experience = State(); activity = State(); days = State(); equipment = State()
    limitations = State(); medical = State(); goal = State(); target_area = State(); measurements = State(); measurement_value = State()


class MeasurementEntry(StatesGroup):
    value = State()


class FoodLookup(StatesGroup):
    search = State()
    portion = State()


class DietarySettings(StatesGroup):
    exclusions = State()


class GoalChange(StatesGroup):
    kind = State()
    target_area = State()
