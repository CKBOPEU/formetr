# Manual smoke test

1. Create a test bot in BotFather and set `BOT_TOKEN` in `.env`.
2. Run `alembic upgrade head`, then `python -m app`.
3. Send `/start` and complete the survey for an adult profile.
4. Verify nutrition and every training day are shown.
5. Open a day, record every exercise with input such as `25 10/10/9 2`.
6. Open the same day again and verify the previous result is displayed.
7. Save weekly measurements at least three times and inspect Progress.
8. Run `/reset` and verify the survey starts again.
9. Repeat with age 17 and verify no calorie deficit is produced.
10. Repeat with pregnancy or an eating-disorder marker and verify the ordinary
    weight-change algorithm is disabled.
