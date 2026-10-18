from datetime import date
from sqlalchemy import delete, select, update
from sqlalchemy.orm import selectinload
from app.database.models import BodyMeasurement, DietaryPreference, Goal, NutritionTarget, ProgressReview, TrainingPlan, User, UserProfile, Workout, WorkoutExercise, WorkoutSet
from app.database.session import session_factory


async def get_user(telegram_id: int) -> User | None:
    async with session_factory()() as session:
        return await session.scalar(select(User).where(User.telegram_id == telegram_id).options(selectinload(User.profile)))


async def reset_user(telegram_id: int) -> None:
    async with session_factory()() as session:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
        if user:
            for model in (WorkoutSet, WorkoutExercise, Workout, TrainingPlan, NutritionTarget, BodyMeasurement, ProgressReview, Goal):
                if model is WorkoutSet:
                    exercise_ids = select(WorkoutExercise.id).join(Workout).where(Workout.user_id == user.id)
                    await session.execute(delete(WorkoutSet).where(WorkoutSet.workout_exercise_id.in_(exercise_ids)))
                elif model is WorkoutExercise:
                    workout_ids = select(Workout.id).where(Workout.user_id == user.id)
                    await session.execute(delete(WorkoutExercise).where(WorkoutExercise.workout_id.in_(workout_ids)))
                elif hasattr(model, "user_id"):
                    await session.execute(delete(model).where(model.user_id == user.id))
            await session.delete(user)
            await session.commit()


async def save_onboarding(telegram_id: int, username: str | None, data: dict, nutrition, plan: dict) -> tuple[int, int]:
    async with session_factory()() as session:
        user = User(telegram_id=telegram_id, username=username)
        session.add(user)
        await session.flush()
        profile = UserProfile(user_id=user.id, name=data["name"], age=data["age"], sex=data["sex"], height_cm=data["height_cm"],
            weight_kg=data["weight_kg"], experience=data["experience"], activity=data["activity"], training_days=data["training_days"],
            equipment=data["equipment"], limitations=data.get("limitations"), medical_flags=data.get("medical_flags"))
        session.add(profile)
        goal = Goal(user_id=user.id, kind=data["goal"], target_area=data.get("target_area"))
        session.add(goal)
        await session.flush()
        training_plan = TrainingPlan(user_id=user.id, goal_id=goal.id, days_per_week=data["training_days"], plan_data=plan)
        session.add(training_plan)
        if nutrition:
            session.add(NutritionTarget(user_id=user.id, goal_id=goal.id, calories=nutrition.calories,
                protein_min=nutrition.protein_min, protein_max=nutrition.protein_max, fat_min=nutrition.fat_min,
                fat_max=nutrition.fat_max, carbs=nutrition.carbs, fiber=nutrition.fiber))
        session.add(BodyMeasurement(user_id=user.id, weight_kg=data["weight_kg"], waist_cm=data.get("waist_cm"),
            hips_cm=data.get("hips_cm"), chest_cm=data.get("chest_cm"), arm_cm=data.get("arm_cm"),
            thigh_cm=data.get("thigh_cm"), calf_cm=data.get("calf_cm")))
        await session.commit()
        return user.id, training_plan.id


async def get_dashboard(telegram_id: int):
    async with session_factory()() as session:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id).options(selectinload(User.profile)))
        if not user:
            return None
        goal = await session.scalar(select(Goal).where(Goal.user_id == user.id, Goal.active.is_(True)).order_by(Goal.id.desc()))
        plan = await session.scalar(select(TrainingPlan).where(TrainingPlan.user_id == user.id, TrainingPlan.active.is_(True)).order_by(TrainingPlan.id.desc()))
        nutrition = await session.scalar(select(NutritionTarget).where(NutritionTarget.user_id == user.id).order_by(NutritionTarget.id.desc()))
        return user, goal, plan, nutrition


async def add_measurement(telegram_id: int, values: dict) -> None:
    async with session_factory()() as session:
        user_id = await session.scalar(select(User.id).where(User.telegram_id == telegram_id))
        if not user_id:
            raise ValueError("User not found")
        session.add(BodyMeasurement(user_id=user_id, measured_on=date.today(), **values))
        await session.commit()


async def measurement_history(telegram_id: int, limit: int = 8) -> list[BodyMeasurement]:
    async with session_factory()() as session:
        user_id = await session.scalar(select(User.id).where(User.telegram_id == telegram_id))
        rows = await session.scalars(select(BodyMeasurement).where(BodyMeasurement.user_id == user_id).order_by(BodyMeasurement.measured_on.desc(), BodyMeasurement.id.desc()).limit(limit))
        return list(reversed(rows.all()))


async def previous_exercise_result(user_id: int, slug: str):
    async with session_factory()() as session:
        query = (select(WorkoutExercise).join(Workout).where(Workout.user_id == user_id, Workout.completed.is_(True), WorkoutExercise.exercise_slug == slug)
                 .options(selectinload(WorkoutExercise.sets)).order_by(Workout.performed_at.desc()).limit(1))
        return await session.scalar(query)


async def save_workout(user_id: int, plan_id: int, day_number: int, entries: list[dict]) -> None:
    async with session_factory()() as session:
        workout = Workout(user_id=user_id, plan_id=plan_id, day_number=day_number, completed=True)
        session.add(workout)
        await session.flush()
        for order, entry in enumerate(entries):
            exercise = WorkoutExercise(workout_id=workout.id, exercise_slug=entry["slug"], order=order)
            session.add(exercise)
            await session.flush()
            for number, reps in enumerate(entry["reps"], 1):
                session.add(WorkoutSet(workout_exercise_id=exercise.id, set_number=number, weight_kg=entry["weight"], reps=reps, rir=entry["rir"]))
        await session.commit()


async def change_plan_data(plan_id: int, plan_data: dict) -> None:
    async with session_factory()() as session:
        await session.execute(update(TrainingPlan).where(TrainingPlan.id == plan_id).values(plan_data=plan_data))
        await session.commit()


async def change_goal(telegram_id: int, kind: str, target_area: str | None, nutrition, plan_data: dict) -> None:
    async with session_factory()() as session:
        user_id = await session.scalar(select(User.id).where(User.telegram_id == telegram_id))
        if not user_id:
            raise ValueError("User not found")
        await session.execute(update(Goal).where(Goal.user_id == user_id, Goal.active.is_(True)).values(active=False))
        await session.execute(update(TrainingPlan).where(TrainingPlan.user_id == user_id, TrainingPlan.active.is_(True)).values(active=False))
        goal = Goal(user_id=user_id, kind=kind, target_area=target_area)
        session.add(goal)
        await session.flush()
        session.add(TrainingPlan(user_id=user_id, goal_id=goal.id, days_per_week=plan_data["days_per_week"], plan_data=plan_data))
        if nutrition:
            session.add(NutritionTarget(user_id=user_id, goal_id=goal.id, calories=nutrition.calories,
                protein_min=nutrition.protein_min, protein_max=nutrition.protein_max,
                fat_min=nutrition.fat_min, fat_max=nutrition.fat_max, carbs=nutrition.carbs, fiber=nutrition.fiber))
        await session.commit()


async def record_review(telegram_id: int, accepted: bool, reason: str, percent: int) -> int | None:
    async with session_factory()() as session:
        user_id = await session.scalar(select(User.id).where(User.telegram_id == telegram_id))
        goal = await session.scalar(select(Goal).where(Goal.user_id == user_id, Goal.active.is_(True)).order_by(Goal.id.desc()))
        if not user_id or not goal:
            raise ValueError("Active profile not found")
        session.add(ProgressReview(user_id=user_id, goal_id=goal.id, decision="adjust" if accepted else "keep",
            reason=reason, proposed_change={"calories_percent": percent}, accepted=accepted))
        new_calories = None
        if accepted and percent:
            current = await session.scalar(select(NutritionTarget).where(NutritionTarget.user_id == user_id, NutritionTarget.goal_id == goal.id).order_by(NutritionTarget.id.desc()))
            if current:
                new_calories = round(current.calories * (1 + percent / 100) / 10) * 10
                carb_delta = round((new_calories - current.calories) / 4)
                session.add(NutritionTarget(user_id=user_id, goal_id=goal.id, calories=new_calories,
                    protein_min=current.protein_min, protein_max=current.protein_max,
                    fat_min=current.fat_min, fat_max=current.fat_max,
                    carbs=max(0, current.carbs + carb_delta), fiber=current.fiber))
        await session.commit()
        return new_calories


async def get_dietary_preferences(telegram_id: int) -> DietaryPreference | None:
    async with session_factory()() as session:
        user_id = await session.scalar(select(User.id).where(User.telegram_id == telegram_id))
        if not user_id:
            return None
        return await session.scalar(select(DietaryPreference).where(DietaryPreference.user_id == user_id))


async def save_dietary_preferences(telegram_id: int, raw_text: str, excluded_foods: list[str]) -> None:
    async with session_factory()() as session:
        user_id = await session.scalar(select(User.id).where(User.telegram_id == telegram_id))
        if not user_id:
            raise ValueError("User not found")
        preference = await session.scalar(select(DietaryPreference).where(DietaryPreference.user_id == user_id))
        if preference:
            preference.raw_text = raw_text
            preference.excluded_foods = excluded_foods
        else:
            session.add(DietaryPreference(user_id=user_id, raw_text=raw_text, excluded_foods=excluded_foods))
        await session.commit()
