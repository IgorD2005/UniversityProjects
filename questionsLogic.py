import json
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql.expression import func

Base = declarative_base()


class WordQuestion(Base):
    __tablename__ = 'word_questions'

    id = Column(Integer, primary_key=True)
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)
    category = Column(String, nullable=False)

engine = create_engine('sqlite:///words.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def load_questions_from_json_and_update(json_path):
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    session = Session()
    new_questions_added = 0
    try:
        for item in data:
            existing_question = session.query(WordQuestion).filter_by(
                question=item['question'],
                answer=item['answer'],
                difficulty=item['difficulty'],
                category=item['category']
            ).first()

            if not existing_question:
                question = WordQuestion(
                    question=item['question'],
                    answer=item['answer'],
                    difficulty=item['difficulty'],
                    category=item['category']
                )
                session.add(question)
                new_questions_added += 1

        session.commit()
        print(
            f"Loaded {new_questions_added} new questions from JSON. Total questions in DB: {session.query(WordQuestion).count()}")
    except Exception as e:
        session.rollback()
        print(f"An error occurred during loading questions: {e}")
    finally:
        session.close()


load_questions_from_json_and_update("word_questions.json")


def get_random_questions(language: str, difficulty: str, limit: int = 10):
    session = Session()
    questions = session.query(WordQuestion).filter_by(category=language, difficulty=difficulty).order_by(
        func.random()).limit(limit).all()
    session.close()
    return questions