# Mad Oauth2

Mad Oauth2 app is an extension of django-oauth-toolkit that implements scopes and schemes in detail

## Quick start

1. Add "mad_oauth2" to your INSTALLED_APPS setting like this:

    ```python
    INSTALLED_APPS = [
        ...
        'oauth2_provider',
        'mad_oauth2',
        ...
    ]

    REST_FRAMEWORK = {
        ...
        "DEFAULT_PERMISSION_CLASSES": (
            "oauth2_provider.contrib.rest_framework.TokenMatchesOASRequirements",
            # OR
            "oauth2_provider.contrib.rest_framework.TokenHasResourceScope",
        ),
        'DEFAULT_THROTTLE_CLASSES': [
            'mad_oauth2.throttling.BaseScopedRateThrottle'
        ],
        ...
    }

    OAUTH2_PROVIDER_APPLICATION_MODEL="mad_oauth2.Application"
    OAUTH2_PROVIDER = {
        "SCOPES_BACKEND_CLASS": "mad_oauth2.oauth2.ApplicationScopes",
        "APPLICATION_ADMIN_CLASS": "mad_oauth2.admin.ApplicationAdminClass",
    }
    ```

2. Run ``python manage.py migrate`` to create mad_oauth2 models.

## Important Note

First add scopes and throttles from the admin, then mark the view with the respective scope. Changes will take effect once the code is deployed(redeployed/rebuild).

## Clearing Expired Tokens

Run celery periodic task to clear expired tokens
`mad_oauth2.tasks.removeExpiredTokens`

## Restricting Views with Scopes

```python
this_view = "user"
throttle_scope = this_view
required_alternate_scopes = mad_oauth2.utils.requiredScopesForView(this_view)
```

Visit the official documentation for `django-oauth-toolkit` for more details on this:

https://django-oauth-toolkit.readthedocs.io/en/latest/rest-framework/permissions.html

## Throttling Requests

```python
REST_FRAMEWORK = {
    ...
    'DEFAULT_THROTTLE_CLASSES': [
        'mad_oauth2.throttling.BaseScopedRateThrottle',
    ],
    ...
}
```

Visit the official documentation for `djangorestframework` for more details this:

https://www.django-rest-framework.org/api-guide/throttling/#scopedratethrottle
