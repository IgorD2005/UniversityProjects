from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()

class Player(Base):
    __tablename__ = 'players'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    games_played = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)

    games = relationship("Game", back_populates="player")


class Game(Base):
    __tablename__ = 'games'

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'))
    score = Column(Integer)
    difficulty = Column(String)
    mode = Column(String)

    player = relationship("Player", back_populates="games")


engine = create_engine('sqlite:///players.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
