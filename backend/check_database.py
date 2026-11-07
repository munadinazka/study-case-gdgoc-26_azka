
from sqlalchemy import select, func

from app.database import SessionLocal
from app.models import (
    User,
    Movie,
    Genre,
    Person,
    MoviePerson,
    Watchlist,
    UserRating,
)


def check_database():
    print("=" * 55)
    print("FILMLOG - DATABASE VERIFICATION")
    print("=" * 55)

    try:
        with SessionLocal() as db:

            # 1. Check total records in all eight tables
            tables = [
                ("users", User),
                ("movies", Movie),
                ("genres", Genre),
                ("movie_genre", None),
                ("people", Person),
                ("movie_people", MoviePerson),
                ("watchlists", Watchlist),
                ("user_ratings", UserRating),
            ]

            print("\n[1] TABLE RECORD COUNTS")

            for table_name, model in tables:
                if table_name == "movie_genre":
                    from app.models import movie_genre

                    statement = select(
                        func.count()
                    ).select_from(movie_genre)

                    count = db.scalar(statement)
                else:
                    count = db.scalar(
                        select(func.count()).select_from(model)
                    )

                print(f"{table_name:<20}: {count}")

            # 2. Check movie records
            print("\n[2] MOVIE DATA")

            movies = db.scalars(
                select(Movie).order_by(Movie.movie_id).limit(5)
            ).all()

            for movie in movies:
                print(
                    f"{movie.movie_id}. {movie.title} "
                    f"({movie.release_year})"
                )

            total_movies = db.scalar(
                select(func.count()).select_from(Movie)
            )

            print(f"Total movies: {total_movies}")

            # 3. Check movie-genre relationships
            print("\n[3] MOVIE-GENRE RELATIONSHIPS")

            first_movie = db.scalars(
                select(Movie)
                .where(Movie.movie_id == 1)
            ).first()

            if first_movie:
                genre_names = [
                    genre.genre_name
                    for genre in first_movie.genres
                ]

                print(f"Movie: {first_movie.title}")
                print(f"Genres: {', '.join(genre_names)}")

            # 4. Check movie-people relationships
            print("\n[4] MOVIE-PEOPLE RELATIONSHIPS")

            if first_movie:
                credits = db.scalars(
                    select(MoviePerson)
                    .where(MoviePerson.movie_id == first_movie.movie_id)
                    .order_by(MoviePerson.role_type, MoviePerson.billing_order)
                ).all()

                for credit in credits:
                    print(
                        f"{credit.role_type}: "
                        f"{credit.person.person_name}"
                    )

            # 5. Check watchlist and ratings tables
            print("\n[5] USER DATA TABLES")

            watchlist_count = db.scalar(
                select(func.count()).select_from(Watchlist)
            )

            rating_count = db.scalar(
                select(func.count()).select_from(UserRating)
            )

            print(f"Watchlists: {watchlist_count}")
            print(f"User ratings: {rating_count}")

        print("\n" + "=" * 55)
        print("DATABASE VERIFICATION COMPLETED!")
        print("=" * 55)

    except Exception as error:
        print("\nDATABASE VERIFICATION FAILED!")
        print(f"Error: {type(error).__name__}: {error}")
        raise


if __name__ == "__main__":
    check_database()
