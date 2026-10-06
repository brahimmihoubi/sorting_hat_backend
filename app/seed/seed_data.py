import logging
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, engine
from app.core.security import get_password_hash
from app.models import AdminUser, Answer, Department, Question, ScoringRule

logger = logging.getLogger("sdg_sorting_hat.seed")


# ----------------------------------------------------
# DEPARTMENTS SEED SPECIFICATION
# ----------------------------------------------------
DEPARTMENTS_SEED = [
    {
        "slug": "development",
        "name": "Development",
        "description": "Focuses on technical thinking, problem solving, building software, web apps, and exploring technology.",
        "short_description": "Technical thinking, problem solving & software development.",
        "icon": "code",
        "color": "#3B82F6",
        "display_order": 1,
    },
    {
        "slug": "design",
        "name": "Design",
        "description": "Focuses on visual identity, UI/UX aesthetics, graphic creation, branding, and creative direction.",
        "short_description": "Creativity, visual aesthetics & design identity.",
        "icon": "palette",
        "color": "#EC4899",
        "display_order": 2,
    },
    {
        "slug": "events",
        "name": "Events",
        "description": "Focuses on leadership, workshop organization, team coordination, logistics, and participant experience.",
        "short_description": "Leadership, event organization & team coordination.",
        "icon": "users",
        "color": "#F59E0B",
        "display_order": 3,
    },
    {
        "slug": "social_media",
        "name": "Social Media",
        "description": "Focuses on communication, public relations, content creation, community engagement, and digital outreach.",
        "short_description": "Communication, promotion & community outreach.",
        "icon": "share-2",
        "color": "#10B981",
        "display_order": 4,
    },
]


# ----------------------------------------------------
# FINAL AUTHORITATIVE QUESTIONNAIRE & SCORING SEED DATA
# ----------------------------------------------------
QUESTIONNAIRE_SEED = [
    {
        "display_order": 1,
        "text": "What kind of work could you spend hours on?",
        "answers": [
            {
                "display_order": 1,
                "text": "Turning ideas into functional things people can use.",
                "rules": [{"dept_slug": "development", "weight": 25.0}],
            },
            {
                "display_order": 2,
                "text": "Exploring layouts, colors, and visuals until they feel right.",
                "rules": [{"dept_slug": "design", "weight": 25.0}],
            },
            {
                "display_order": 3,
                "text": "Planning experiences that bring people together.",
                "rules": [{"dept_slug": "events", "weight": 25.0}],
            },
            {
                "display_order": 4,
                "text": "Creating content and ideas that grab attention.",
                "rules": [{"dept_slug": "social_media", "weight": 25.0}],
            },
        ],
    },
    {
        "display_order": 2,
        "text": "When facing a new challenge, what catches your attention first?",
        "answers": [
            {
                "display_order": 1,
                "text": "Understanding the problem and figuring out how to fix it.",
                "rules": [{"dept_slug": "development", "weight": 25.0}],
            },
            {
                "display_order": 2,
                "text": "Finding an original or visually interesting approach.",
                "rules": [{"dept_slug": "design", "weight": 25.0}],
            },
            {
                "display_order": 3,
                "text": "Understanding people and getting them on board.",
                "rules": [{"dept_slug": "social_media", "weight": 25.0}],
            },
            {
                "display_order": 4,
                "text": "Figuring out what needs to happen and how everything fits together.",
                "rules": [{"dept_slug": "events", "weight": 25.0}],
            },
        ],
    },
    {
        "display_order": 3,
        "text": "What motivates you in a project?",
        "answers": [
            {
                "display_order": 1,
                "text": "Seeing an idea become something useful that solves a problem.",
                "rules": [{"dept_slug": "development", "weight": 25.0}],
            },
            {
                "display_order": 2,
                "text": "Creating something distinctive, polished, and memorable.",
                "rules": [{"dept_slug": "design", "weight": 25.0}],
            },
            {
                "display_order": 3,
                "text": "Seeing everyone contribute and achieve something together.",
                "rules": [{"dept_slug": "events", "weight": 25.0}],
            },
            {
                "display_order": 4,
                "text": "Reaching people, making them think, or inspiring them to get involved.",
                "rules": [{"dept_slug": "social_media", "weight": 25.0}],
            },
        ],
    },
    {
        "display_order": 4,
        "text": "When a project stops making sense, what's your instinct?",
        "answers": [
            {
                "display_order": 1,
                "text": "Break the problem down and find where things went wrong.",
                "rules": [{"dept_slug": "development", "weight": 25.0}],
            },
            {
                "display_order": 2,
                "text": "Try different approaches until something works.",
                "rules": [
                    {"dept_slug": "development", "weight": 20.0},
                    {"dept_slug": "design", "weight": 10.0},
                ],
            },
            {
                "display_order": 3,
                "text": "Talk it through with others to understand what you're missing.",
                "rules": [
                    {"dept_slug": "events", "weight": 20.0},
                    {"dept_slug": "social_media", "weight": 10.0},
                ],
            },
            {
                "display_order": 4,
                "text": "Step back, reorganize everything, and establish a clearer way forward.",
                "rules": [
                    {"dept_slug": "events", "weight": 20.0},
                    {"dept_slug": "development", "weight": 10.0},
                ],
            },
        ],
    },
    {
        "display_order": 5,
        "text": "You can choose any SDG project. What would you pick?",
        "answers": [
            {
                "display_order": 1,
                "text": "Create something digital that makes a process easier or more useful.",
                "rules": [{"dept_slug": "development", "weight": 25.0}],
            },
            {
                "display_order": 2,
                "text": "Create the visual identity that defines a project.",
                "rules": [{"dept_slug": "design", "weight": 25.0}],
            },
            {
                "display_order": 3,
                "text": "Make an SDG initiative visible and engaging to a wider audience.",
                "rules": [{"dept_slug": "social_media", "weight": 25.0}],
            },
            {
                "display_order": 4,
                "text": "Create an activity where people can participate and have a memorable experience.",
                "rules": [{"dept_slug": "events", "weight": 25.0}],
            },
        ],
    },
    {
        "display_order": 6,
        "text": "How comfortable are you taking the lead?",
        "answers": [
            {
                "display_order": 1,
                "text": "Support someone else's direction.",
                "rules": [{"trait": "leadership", "trait_value": 0.40, "dept_slug": "events", "weight": 10.0}],
            },
            {
                "display_order": 2,
                "text": "Helping only when needed.",
                "rules": [{"trait": "leadership", "trait_value": 0.40, "dept_slug": "events", "weight": 10.0}],
            },
            {
                "display_order": 3,
                "text": "Often naturally step forward.",
                "rules": [{"trait": "leadership", "trait_value": 0.70, "dept_slug": "events", "weight": 17.5}],
            },
            {
                "display_order": 4,
                "text": "Enjoy taking responsibility and guiding the team.",
                "rules": [{"trait": "leadership", "trait_value": 0.90, "dept_slug": "events", "weight": 22.5}],
            },
        ],
    },
    {
        "display_order": 7,
        "text": "In a team project, where do you naturally fit?",
        "answers": [
            {
                "display_order": 1,
                "text": "Turning the team's ideas into something concrete and workable.",
                "rules": [{"dept_slug": "development", "weight": 25.0}],
            },
            {
                "display_order": 2,
                "text": "Exploring possibilities and imagining how the final result could look, feel, or work.",
                "rules": [{"dept_slug": "design", "weight": 25.0}],
            },
            {
                "display_order": 3,
                "text": "Thinking about how to explain the idea, attract interest, and get the message across.",
                "rules": [{"dept_slug": "social_media", "weight": 25.0}],
            },
            {
                "display_order": 4,
                "text": "Bringing people together, setting responsibilities, and keeping things moving.",
                "rules": [{"dept_slug": "events", "weight": 25.0}],
            },
        ],
    },
    {
        "display_order": 8,
        "text": "What would you like to learn?",
        "answers": [
            {
                "display_order": 1,
                "text": "Turning an idea into a working digital solution.",
                "rules": [{"dept_slug": "development", "weight": 25.0}],
            },
            {
                "display_order": 2,
                "text": "Turning an ordinary idea into something visually distinctive and memorable.",
                "rules": [{"dept_slug": "design", "weight": 25.0}],
            },
            {
                "display_order": 3,
                "text": "Expressing an idea clearly and creatively so people want to listen, participate, or share.",
                "rules": [{"dept_slug": "social_media", "weight": 25.0}],
            },
            {
                "display_order": 4,
                "text": "Turning a group's energy into a successful project.",
                "rules": [{"dept_slug": "events", "weight": 25.0}],
            },
        ],
    },
]


def seed_db(db: Session) -> None:
    """Idempotently seed the database with departments, questions, answers, and scoring rules."""
    logger.info("Starting database seed process...")

    # 1. Seed Departments
    dept_map = {}
    for d_data in DEPARTMENTS_SEED:
        dept = db.query(Department).filter(Department.slug == d_data["slug"]).first()
        if not dept:
            dept = Department(**d_data)
            db.add(dept)
            db.flush()
            logger.info(f"Created department: {dept.name}")
        else:
            for key, val in d_data.items():
                setattr(dept, key, val)
            logger.info(f"Updated department: {dept.name}")
        dept_map[dept.slug] = dept

    # 2. Seed Questions & Answers & ScoringRules
    for q_data in QUESTIONNAIRE_SEED:
        q_order = q_data["display_order"]
        q_text = q_data["text"]

        question = db.query(Question).filter(Question.display_order == q_order).first()
        if not question:
            question = Question(text=q_text, display_order=q_order, type="single_choice", required=True, active=True)
            db.add(question)
            db.flush()
            logger.info(f"Created Question Q{q_order}")
        else:
            question.text = q_text
            question.active = True

        for a_data in q_data["answers"]:
            a_order = a_data["display_order"]
            a_text = a_data["text"]

            answer = (
                db.query(Answer)
                .filter(Answer.question_id == question.id, Answer.display_order == a_order)
                .first()
            )
            if not answer:
                answer = Answer(
                    question_id=question.id,
                    text=a_text,
                    display_order=a_order,
                    active=True,
                )
                db.add(answer)
                db.flush()
            else:
                answer.text = a_text
                answer.active = True

            # Clear existing scoring rules for this answer to allow idempotent updates
            db.query(ScoringRule).filter(ScoringRule.answer_id == answer.id).delete()

            # Create updated scoring rules
            for rule_data in a_data["rules"]:
                target_dept = dept_map.get(rule_data.get("dept_slug"))
                rule = ScoringRule(
                    question_id=question.id,
                    answer_id=answer.id,
                    department_id=target_dept.id if target_dept else None,
                    weight=rule_data.get("weight", 0.0),
                    trait=rule_data.get("trait"),
                    trait_value=rule_data.get("trait_value"),
                )
                db.add(rule)

    # 3. Seed Default Admin User
    admin_email = "admin@sdg.dz"
    admin = db.query(AdminUser).filter(AdminUser.email == admin_email).first()
    if not admin:
        admin = AdminUser(
            name="SDG Admin",
            email=admin_email,
            password_hash=get_password_hash("admin123"),
            role="super_admin",
            active=True,
        )
        db.add(admin)
        logger.info(f"Created default admin user: {admin_email}")

    db.commit()
    logger.info("Database seeding completed successfully!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    db = SessionLocal()
    try:
        seed_db(db)
    finally:
        db.close()
