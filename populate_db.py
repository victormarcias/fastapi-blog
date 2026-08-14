import asyncio
from datetime import UTC, datetime, timedelta
from pathlib import Path

import httpx
from sqlalchemy import delete, select, update

import models
from models import Base
from config import settings
from database import AsyncSessionLocal, engine
from main import app

POPULATE_IMAGES_DIR = Path("mocks/populate_images")

USERS = [
    {
        "username": "Wolverine",
        "email": "wolverine@test.com",
        "password": "Password1!",
        "image": "wolverine.jpg",
    },
    {
        "username": "Victor",
        "email": "victor@test.com",
        "password": "Password1!",
    },
    {
        "username": "Conejo",
        "email": "conejo@test.com",
        "password": "Password1!",
        "image": "thanos-bunny.jpg",
    },
    {
        "username": "TheBatman",
        "email": "thebatman@test.com",
        "password": "Password1!",
        "image": "the-batman.jpg",
    },
    {
        "username": "DocEmmettBrown",
        "email": "docbrown@test.com",
        "password": "Password1!",
        "image": "emmett-brown.jpg",
    },
    {
        "username": "Thanos",
        "email": "thanos@test.com",
        "password": "Password1!",
        "image": "thanos.jpg",
    },
]

POSTS = [
    {
        "title": "Say Hello to My Little Friend",
        "content": "Tony Montana in 'Scarface': \"Say hello to my little friend!\" Been rewatching gangster classics lately and this one still holds up 40+ years later. Pacino's performance is unmatched.",
    },
    {
        "title": "Reality Is Often Disappointing",
        "content": "Thanos in 'Avengers: Infinity War': \"Reality is often disappointing.\" Say what you want about the guy's methods, but Josh Brolin brought a weirdly compelling weight to a CGI villain.",
    },
    {
        "title": "It's Not Who I Am Underneath",
        "content": "Bruce Wayne in 'Batman Begins': \"It's not who I am underneath, but what I do that defines me.\" Nolan's trilogy took superhero movies seriously in a way nothing before it did.",
    },
    {
        "title": "Roads? Where We're Going...",
        "content": "Doc Brown in 'Back to the Future': \"Roads? Where we're going, we don't need roads.\" Still one of the best closing lines in movie history. DeLorean gull-wing doors will never not be cool.",
    },
    {
        "title": "I'll Be Back",
        "content": "The Terminator in 'The Terminator': \"I'll be back.\" Three words, endless parodies, and Arnold's most iconic line to this day.",
    },
    {
        "title": "Hasta La Vista, Baby",
        "content": "The T-800 in 'Terminator 2: Judgment Day': \"Hasta la vista, baby.\" A rare case where the sequel's catchphrase outshines the original's. Arguably the best action sequel ever made.",
    },
    {
        "title": "An Offer He Can't Refuse",
        "content": "Vito Corleone in 'The Godfather': he'll make him an offer he can't refuse. Still the gold standard for crime dramas. Brando's whole performance is a masterclass in restraint.",
    },
    {
        "title": "Why So Serious?",
        "content": "The Joker in 'The Dark Knight': \"Why so serious?\" Heath Ledger's performance is one of those rare cases where the hype is completely justified. Chilling every single time.",
    },
    {
        "title": "Life Finds a Way",
        "content": "Dr. Ian Malcolm in 'Jurassic Park': \"Life finds a way.\" Simple line, but it kind of sums up the entire premise of the franchise. Also the best Jeff Goldblum has ever been.",
    },
    {
        "title": "Life Is Like a Box of Chocolates",
        "content": 'Forrest Gump: "Life is like a box of chocolates." Corny? Maybe. But this movie gets me every single time, no matter how many times I\'ve seen it.',
    },
    {
        "title": "The Desert of the Real",
        "content": "Morpheus in 'The Matrix': welcoming Neo to \"the desert of the real.\" A movie that got smarter and weirder every time I rewatched it as I got older. Still holds up 25+ years later.",
    },
    {
        "title": "You're Gonna Need a Bigger Boat",
        "content": "Chief Brody in 'Jaws': \"You're gonna need a bigger boat.\" Improvised on set, and it became one of the most quoted lines in movie history. Spielberg at his tension-building best.",
    },
    {
        "title": "You Talkin' to Me?",
        "content": "Travis Bickle in 'Taxi Driver': \"You talkin' to me?\" De Niro reportedly improvised most of that scene. One of those moments where you can feel an actor completely disappear into a role.",
    },
    {
        "title": "Here's Looking at You, Kid",
        "content": "Rick Blaine in 'Casablanca': \"Here's looking at you, kid.\" Old Hollywood romance doesn't get more iconic than this. The whole movie is quotable start to finish.",
    },
    {
        "title": "Are You Not Entertained?",
        "content": "Maximus in 'Gladiator': \"Are you not entertained?\" One of the best revenge arcs put to film. Hans Zimmer's score alone could carry the whole movie.",
    },
    {
        "title": "Yo, Adrian!",
        "content": "Rocky Balboa's iconic call out to Adrian. The original 'Rocky' is such a simple underdog story, but it works every single time. Sometimes the classics are classics for a reason.",
    },
    {
        "title": "Here's Johnny!",
        "content": "Jack Torrance in 'The Shining': \"Here's Johnny!\" Nicholson improvised that line referencing a talk show intro, and it became one of horror's most famous moments. Kubrick's slow-burn dread is unmatched.",
    },
    {
        "title": "If You Build It, He Will Come",
        "content": "The whispered voice in 'Field of Dreams': \"If you build it, he will come.\" A movie about baseball that somehow isn't really about baseball at all. Gets me every time.",
    },
    {
        "title": "Houston, We Have a Problem",
        "content": "Jim Lovell in 'Apollo 13': \"Houston, we have a problem.\" A tense, based-on-true-events thriller where you already know the outcome and it still grips you the whole way through.",
    },
    {
        "title": "Hello, Clarice",
        "content": "Hannibal Lecter greeting Clarice Starling in 'The Silence of the Lambs.' Anthony Hopkins is on screen for a tiny fraction of the runtime and still dominates the entire movie.",
    },
    {
        "title": "They'll Never Take Our Freedom",
        "content": "William Wallace in 'Braveheart': they may take our lives, but they'll never take our freedom. Say what you want about historical accuracy, the speech still gives me chills.",
    },
    {
        "title": "The Need for Speed",
        "content": "Maverick in 'Top Gun': talking about the need for speed. Pure 80s cheese in the best possible way. The Tom Cruise sequel decades later somehow topped the original.",
    },
    {
        "title": "You Can't Handle the Truth",
        "content": "Col. Jessup in 'A Few Good Men': \"You can't handle the truth!\" Jack Nicholson chewing scenery has never been more entertaining. That courtroom scene is a masterclass in tension.",
    },
    {
        "title": "Greed Is Good",
        "content": "Gordon Gekko in 'Wall Street': greed, for lack of a better word, is good. A speech meant as a warning that half the finance world apparently took as a mission statement.",
    },
    {
        "title": "Go Ahead, Make My Day",
        "content": "Harry Callahan in 'Sudden Impact': \"Go ahead, make my day.\" Clint Eastwood at his most quotable. The whole Dirty Harry series is full of one-liners like this.",
    },
    {
        "title": "E.T. Phone Home",
        "content": "E.T.'s simple request: phone home. Spielberg somehow made a rubber puppet one of the most emotionally resonant characters in movie history. Still gets me at the ending.",
    },
    {
        "title": "Life Moves Pretty Fast",
        "content": "Ferris Bueller reminding us that life moves pretty fast, and if you don't stop and look around once in a while, you could miss it. Good advice, honestly.",
    },
    {
        "title": "Show Me the Money!",
        "content": 'Jerry Maguire and Rod Tidwell\'s back-and-forth: "Show me the money!" One of those phrases that escaped the movie entirely and became part of everyday vocabulary.',
    },
    {
        "title": "There's No Place Like Home",
        "content": "Dorothy in 'The Wizard of Oz': there's no place like home. A movie from 1939 that somehow still holds up as a piece of pure imagination and technicolor spectacle.",
    },
    {
        "title": "Frankly, My Dear...",
        "content": "Rhett Butler's parting line in 'Gone with the Wind': frankly, he doesn't give a damn. One of the most famous closing lines in film history, and still controversial for the time it was said.",
    },
    {
        "title": "Failure to Communicate",
        "content": "The Captain in 'Cool Hand Luke': what we've got here is failure to communicate. A quietly devastating line from a movie that's mostly about quiet defiance.",
    },
    {
        "title": "Mad as Hell",
        "content": "Howard Beale in 'Network': declaring he's mad as hell. A movie from the 70s that somehow predicted modern media better than anything made since. Genuinely unsettling how accurate it got.",
    },
    {
        "title": "King of the World",
        "content": "Jack Dawson on the bow of the ship in 'Titanic': declaring himself king of the world. Corny in hindsight, but there's a reason this scene became instantly iconic.",
    },
    {
        "title": "Our Independence Day",
        "content": "President Whitmore's speech in 'Independence Day': rallying the world by calling it our independence day. Peak 90s summer blockbuster. Will Smith punching an alien remains a top-tier movie moment.",
    },
    {
        "title": "My Name Is Inigo Montoya",
        "content": "Inigo Montoya in 'The Princess Bride' introducing himself before every duel. One of the most quotable movies ever made, and somehow also genuinely funny, romantic, and thrilling all at once.",
    },
    {
        "title": "Stay Classy, San Diego",
        "content": "Ron Burgundy signing off with \"stay classy, San Diego.\" 'Anchorman' might be one of the most quoted comedies of the 2000s. Still makes me laugh out loud.",
    },
    {
        "title": "That's So Fetch",
        "content": "Gretchen Wieners in 'Mean Girls' trying (and failing) to make \"fetch\" happen. A movie that somehow got funnier and more quotable with each passing year since it came out.",
    },
    {
        "title": "Blue Steel",
        "content": "Derek Zoolander showing off his signature look: Blue Steel. 'Zoolander' is dumb in the best possible way. A comedy that fully commits to its own absurdity.",
    },
    {
        "title": "I Am Iron Man",
        "content": "Tony Stark's closing line in the first 'Iron Man': \"I am Iron Man.\" The moment that basically kicked off an entire decade of superhero movies as we know them.",
    },
    {
        "title": "A Royale With Cheese",
        "content": "Vincent Vega in 'Pulp Fiction' explaining what they call a Quarter Pounder in France: a Royale with cheese. Tarantino turning a fast food conversation into one of cinema's most quoted scenes.",
    },
    {
        "title": "I Must Break You",
        "content": "Ivan Drago in 'Rocky IV': \"I must break you.\" Maybe five lines of dialogue in the entire movie, and somehow still one of the most memorable villains in the franchise.",
    },
    {
        "title": "I See Dead People",
        "content": "Cole Sear in 'The Sixth Sense': \"I see dead people.\" The twist ending held up remarkably well for a movie that basically invented the modern twist-ending genre.",
    },
    {
        "title": "Movie Quotes!",
        "content": "'You wanna know how I did it? This is how I did it, Anton. I never saved anything for the swim back.' - 'Gattaca'. One of my favorite movies of all time. As silly as it sounds, that movie is actually one of the main reasons I decided to pursue an internship at NASA back in college. After that internship, I found I had a craving to learn and do more. It pushed me to take programming more seriously, which eventually led me to where I am today... Which is writing a blog post about FastAPI that's just meant to fill space. TLDR: I watched Gattaca and now I'm writing sample blog posts at 3am on a Saturday for this FastAPI tutorial. And you can too!",
    },
]

# The 44th post - always the oldest (easter egg for pagination tutorial)
POST_44 = {
    "title": "Fun Fact: My High School Football Number Was #44",
    "content": "If you've paginated all the way to this post, the 44th one... you get to learn this fun fact: that my high school football number was #44. Other notable absolute legends who wore number #44 include: Jerry West (NBA - Also fellow WV Native), Hank Aaron (MLB), and Floyd Little (NFL).",
}


#
#
async def clear_existing_data() -> None:
    # Clear database tables (order respects foreign keys)
    async with AsyncSessionLocal() as db:
        await db.execute(delete(models.PasswordResetToken))
        await db.execute(delete(models.Post))
        await db.execute(delete(models.User))
        await db.commit()
    print("Cleared existing data")


#
#
async def update_post_dates() -> None:
    now = datetime.now(UTC)

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(models.Post).order_by(models.Post.id))
        posts = result.scalars().all()

        if not posts:
            return

        # First post (POST_44) is the oldest - ~90 days ago
        await db.execute(
            update(models.Post)
            .where(models.Post.id == posts[0].id)
            .values(date_posted=now - timedelta(days=90)),
        )

        # Remaining posts: each ~1.5 days newer than previous
        for i, post in enumerate(posts[1:], start=1):
            days_ago = (len(posts) - i) * 1.5
            hours_offset = (i * 7) % 24
            post_date = now - timedelta(days=days_ago, hours=hours_offset)
            await db.execute(
                update(models.Post)
                .where(models.Post.id == post.id)
                .values(date_posted=post_date),
            )

        await db.commit()
    print("Updated post dates")


#
#
async def populate() -> None:
    # simular el startup del host para que funcione el populate aunque no haya corrido antes
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://localhost",
    ) as client:
        # Clear existing data (local images first, then database)
        await clear_existing_data()

        users: list[dict] = []

        print(f"\nCreating {len(USERS)} users...")
        for user_data in USERS:
            response = await client.post(
                f"{settings.base_path}/api/users",
                json={
                    "username": user_data["username"],
                    "email": user_data["email"],
                    "password": user_data["password"],
                },
            )
            response.raise_for_status()
            user = response.json()
            print(f"  Created: {user['username']}")

            response = await client.post(
                f"{settings.base_path}/api/users/token",
                data={
                    "username": user_data["email"],
                    "password": user_data["password"],
                },
            )
            response.raise_for_status()
            token = response.json()["access_token"]

            if image_name := user_data.get("image"):
                image_path = POPULATE_IMAGES_DIR / image_name
                if image_path.exists():
                    response = await client.patch(
                        f"{settings.base_path}/api/users/{user['id']}/picture",
                        files={
                            "file": (
                                image_name,
                                image_path.read_bytes(),
                                "image/png",
                            ),
                        },
                        headers={"Authorization": f"Bearer {token}"},
                    )
                    response.raise_for_status()
                    print(f"    Uploaded: {image_name}")

            users.append(
                {"id": user["id"], "username": user["username"], "token": token},
            )

        print(f"\nCreating {len(POSTS) + 1} posts...")

        # First create POST_44 (will become oldest after date update)
        response = await client.post(
            f"{settings.base_path}/api/posts",
            json={"title": POST_44["title"], "content": POST_44["content"]},
            headers={"Authorization": f"Bearer {users[0]['token']}"},
        )
        response.raise_for_status()
        print(f"  Created: '{POST_44['title']}'")

        # Create remaining posts in reverse (last in list = oldest, first = newest)
        for i, post_data in enumerate(reversed(POSTS)):
            user = users[i % len(users)]
            response = await client.post(
                f"{settings.base_path}/api/posts",
                json={
                    "title": post_data["title"],
                    "content": post_data["content"],
                },
                headers={"Authorization": f"Bearer {user['token']}"},
            )
            response.raise_for_status()
            title = post_data["title"]
            print(
                f"  Created: '{title[:50]}...'"
                if len(title) > 50
                else f"  Created: '{title}'",
            )

        print("\nUpdating post dates...")
        await update_post_dates()

    await engine.dispose()

    print("\nDone!")
    print(f"  {len(USERS)} users")
    print(f"  {len(POSTS) + 1} posts")
    print("  Profile pictures saved locally")


#
#
if __name__ == "__main__":
    asyncio.run(populate())
