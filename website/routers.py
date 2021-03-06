class StatbotRouter:
    """
    Determines the model to be used for models.
    If the model is is a model specified in `stats.models` -
    that is, one of the autogenerated models imported
    from statbot, it will use the statbot database.
    Otherwise, it will use the `default` database.
    """

    def allow_migrate(self, db, app_label, _model_name=None, **_hints):
        return not (
            db == "stats"
            and app_label != "stats"
            or app_label == "stats"
            and db != "stats"
        )

    def db_for_read(self, model, **_hints):
        if model._meta.app_label == "stats":
            return "stats"
        return "default"

    def db_for_write(self, model, **_hints):
        if model._meta.app_label == "stats":
            return "stats"
        return "default"
