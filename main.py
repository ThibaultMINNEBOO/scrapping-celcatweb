import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy import create_engine, Column, String
import pymysql
import dotenv
import os

pymysql.install_as_MySQLdb()

dotenv.load_dotenv()

print(os.getenv('DATABASE_URL'))

engine = create_engine(os.getenv('DATABASE_URL'), echo=True)


class Base(DeclarativeBase):
    pass


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    module: Mapped[str] = mapped_column(String(7))
    fullname: Mapped[str] = mapped_column(String(100))
    type: Mapped[str] = mapped_column(String(50))
    week: Mapped[int] = mapped_column()
    room: Mapped[str] = mapped_column(String(90))
    day: Mapped[int] = mapped_column()
    group: Mapped[str] = mapped_column(String(50))
    teacher: Mapped[str] = mapped_column(String(150))
    hDeb: Mapped[str] = mapped_column(String(20))
    hFin: Mapped[str] = mapped_column(String(20))


Base.metadata.create_all(engine)

for week in range(36, 67):
    if week >= 53:
        week -= 52

    print(f"Semaine {week}")

    for day in range(1, 7):

        print(f"Jour {day}")

        URL = f"http://intranet/celcatweb/index.php?dpt=001&week={week}&day={day}&room=0&group=0&staff=0&module=0"
        page = requests.get(URL)

        soup = BeautifulSoup(page.content, "html.parser")
        events = soup.find_all("div", class_="event")

        for event in events:
            group = event.find_next('ul', class_="groups").find_next('a').text.strip()
            teacher = event.find_next('ul', class_="profs").find_next('a').text.strip()
            module = event.find_next('ul', class_="module").find_next('a').text.strip()
            hours = [event.find_next('h3', class_="heures").find_next('span', class_='hdeb').text.strip(),
                     event.find_next('h3', class_="heures").find_next('span', class_="hfin").text.strip()]
            typeCourse = event.find_next('h3', class_="heures").find_next('span', class_="type").text.strip().replace(
                '[', '').replace(']', '')
            room = event.find_next('ul', 'rooms').find_next('a').text.strip().split("_")[0]

            if not group.startswith('INF') or not module.startswith('M'):
                continue

            with Session(engine) as session:
                newEvent = Event(module=module.split(" ")[0],
                                 fullname=" ".join(module.split(" ")[1:]),
                                 group=group,
                                 teacher=teacher,
                                 type=typeCourse,
                                 week=week,
                                 day=day,
                                 room=room,
                                 hDeb=hours[0],
                                 hFin=hours[1])

                session.add(newEvent)

                session.commit()

