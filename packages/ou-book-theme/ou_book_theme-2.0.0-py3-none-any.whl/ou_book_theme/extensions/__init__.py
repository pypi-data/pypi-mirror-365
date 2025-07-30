from ou_book_theme.extensions import activity, errata, time, video, where_next


def setup(app):
    """Setup all node extensions."""
    activity.setup(app)
    errata.setup(app)
    time.setup(app)
    video.setup(app)
    where_next.setup(app)
