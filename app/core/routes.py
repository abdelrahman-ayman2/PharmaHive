from flask import Blueprint, render_template, session, url_for, Response
from xml.etree.ElementTree import Element, SubElement, tostring
from datetime import datetime, timezone
from ..models.post import Post
from ..models.user import User
from ..models.like import Like
from ..extensions import db
core_bp = Blueprint('core', __name__)


@core_bp.route('/')
def home():
    user_id = session.get("user_id")

    if user_id:
        user = db.session.get(User, user_id)
    else:
        user = None
    
    if user:
        likes = db.session.query(Like.post_id).filter_by(user_id=user.id).all()
        liked_post_ids = {post_id for (post_id,) in likes}
    else:
        liked_post_ids = set()

    posts = Post.query.order_by(Post.created_at.desc()).all()

    return render_template('core/home.html', posts=posts, user=user, liked_post_ids=liked_post_ids)

@core_bp.route("/sitemap.xml", methods=["GET"])
def sitemap():
    pages = []

    static_pages = [
        ("core.home", {}),
        ("auth.login", {}),
        ("auth.register", {}),
    ]

    for endpoint, values in static_pages:
        pages.append({
            "loc": url_for(endpoint, _external=True, **values),
            "lastmod": datetime.now(timezone.utc).date().isoformat(),
            "changefreq": "daily",
            "priority": "1.0" if endpoint == "core.home" else "0.3"
        })

    users = db.session.query(User.username, User.created_at).all()
    for username, created_at in users:
        pages.append({
            "loc": url_for("users.profile", username=username, _external=True),
            "lastmod": (created_at.date().isoformat() if created_at else ""),
            "changefreq": "weekly",
            "priority": "0.7"
        })

    urlset = Element('urlset', xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    for page in pages:
        url = SubElement(urlset, 'url')
        SubElement(url, 'loc').text = page["loc"]
        SubElement(url, 'lastmod').text = page["lastmod"]
        SubElement(url, 'changefreq').text = page["changefreq"]
        SubElement(url, 'priority').text = page["priority"]

    xml = tostring(urlset, encoding='utf-8', method='xml')

    return Response(xml, mimetype="application/xml")

@core_bp.route("/robots.txt", methods=["GET"])
def robots():
    return Response(
        "User-agent: *\nAllow: /\nSitemap: https://pharmahive.xyz/sitemap.xml\n",
        mimetype="text/plain"
    )