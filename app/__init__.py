"""VulnBank — a small invoice portal for freelancers and small teams."""

from __future__ import annotations

import os

from flask import Flask

from .db import close_db, init_db


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.secret_key = "supersecret123"
    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, "vulnbank.sqlite"),
        UPLOAD_DIR=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "uploads"),
    )
    if test_config:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_DIR"], exist_ok=True)

    from . import admin, auth, routes
    app.register_blueprint(auth.bp)
    app.register_blueprint(routes.bp)
    app.register_blueprint(admin.bp)

    app.teardown_appcontext(close_db)

    @app.cli.command("init-db")
    def init_db_command() -> None:
        init_db()
        print("Database initialised.")

    return app
