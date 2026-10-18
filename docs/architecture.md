# FORMETR architecture

`app/bot` is only the Telegram presentation and FSM layer. It parses user input,
calls services and repositories, and formats results. It must not contain energy,
macro, progression or trend formulas.

`app/calculations` contains deterministic pure functions. They can later be used
by a Mini App, HTTP API or an LLM tool without importing aiogram.

`app/services` coordinates domain operations such as plan generation. Exercise
selection is rule-based and uses the catalog in `app/exercises`.

`app/database` owns SQLAlchemy models, sessions and repositories. Goals and plans
are separate historical records; measurement and workout history is append-only
during normal use.

The bot is not a medical device. Adult calorie targets use Mifflin–St Jeor and
activity multipliers, impose a calorie floor, and are disabled for minors and
medical-risk answers. No algorithm infers a working weight from sex or body size.
