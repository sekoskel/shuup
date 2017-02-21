# -*- coding: utf-8 -*-
import shuup.apps


class AppConfig(shuup.apps.AppConfig):
    name = "shuup_form_dfesigner"
    provides = {
        "form_definition": ["shuup_form_designer.models.FormDefinition"],
    }
