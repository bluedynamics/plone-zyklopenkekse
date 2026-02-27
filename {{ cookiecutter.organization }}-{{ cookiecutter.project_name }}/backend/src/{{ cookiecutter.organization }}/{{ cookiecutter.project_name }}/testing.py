from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneWithPackageLayer

import {{ cookiecutter.organization }}.{{ cookiecutter.project_name }}

BASENAME = "{{ cookiecutter.__python_package }}Layer"

FIXTURE = PloneWithPackageLayer(
    bases=(PLONE_APP_CONTENTTYPES_FIXTURE,),
    name=f"{BASENAME}:Fixture",
    gs_profile_id="{{ cookiecutter.__python_package }}:default",
    zcml_package={{ cookiecutter.organization }}.{{ cookiecutter.project_name }},
    zcml_filename="configure.zcml",
)

INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name=f"{BASENAME}:IntegrationTesting",
)

FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,),
    name=f"{BASENAME}:FunctionalTesting",
)
