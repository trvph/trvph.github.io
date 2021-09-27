from jinja2 import Environment, FileSystemLoader
from jinja2.environment import Template
from markdown2 import markdown
from pathlib import Path, PosixPath
from datetime import datetime
from os.path import dirname
import os
import typing as t


# path
root = Path(__file__).parent  # project's path
posts_folder = root.joinpath("./_posts").resolve()  # project/posts/


# read markdown file then write to a dict
def create_posts(paths: Path):
    posts = {}
    for md_post in paths.iterdir():
        with open(md_post.resolve(), "r") as f:
            posts[md_post] = markdown(f.read(), extras=["metadata"])

    # return a dict with sorted following date created
    return {
        p: posts[p]
        for p in sorted(
            posts,
            key=lambda p: datetime.strptime(
                posts[p].metadata["date"], "%d-%m-%Y"
            ),
            reverse=True,
        )
    }


# render homepage
def render_home(outputs_folder: Path, tags: t.List[str], template: Template):
    """Render home.html file to root folder."""

    home_html = template.render(metas=posts_metadata, tags=tags)
    home_path = outputs_folder.joinpath("index.html").resolve()
    with open(home_path, "w") as f:
        f.write(home_html)


# render posts
def render_posts(
    posts: dict, tags: t.List[str], outputs_folder: Path, template: Template
):
    """Render post_metadata['name'].html file to outputs/ folder."""

    for p in posts:
        post_metadata = posts[p].metadata

        post_data = {
            "title": post_metadata["title"],
            "date": post_metadata["date"],
            "content": posts[p],
        }
        post_html = template.render(post=post_data)

        # render to html files
        post_path = outputs_folder.joinpath(
            f"{post_metadata['title']}.html"
        ).resolve()
        os.makedirs(dirname(post_path), exist_ok=True)
        with open(post_path, "w") as f:
            f.write(post_html)


if __name__ == "__main__":
    posts = create_posts(posts_folder)  # get all posts in ./posts/ folder

    # get template environment
    env = Environment(loader=FileSystemLoader(searchpath="./templates"))
    home_template = env.get_template("home.html")
    post_template = env.get_template("post.html")

    posts_metadata = [posts[p].metadata for p in posts]  # all posts metadatas
    tags = [p["tags"] for p in posts_metadata]  # get posts tags

    outputs_folder = root.joinpath("outputs/").resolve()
    render_home(root.resolve(), tags, home_template)
    render_posts(posts, tags, outputs_folder, post_template)