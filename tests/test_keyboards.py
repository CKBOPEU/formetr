from app.bot.keyboards import plan_actions


def test_plan_actions_use_video_links_without_weight_logging() -> None:
    plan = {
        "days": [{
            "day": 1,
            "exercises": [{"slug": "goblet_squat", "name": "Гоблет-присед"}],
        }]
    }

    keyboard = plan_actions(plan)
    buttons = [button for row in keyboard.inline_keyboard for button in row]

    assert all("Вес" not in button.text for button in buttons)
    assert not any(button.callback_data and button.callback_data.startswith("workout:") for button in buttons)
    assert any(button.url and "youtube.com/results" in button.url for button in buttons)
    assert any(button.callback_data == "replace:1:goblet_squat" for button in buttons)
