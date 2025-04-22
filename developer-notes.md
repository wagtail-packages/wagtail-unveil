# Investigate the modeladmin registration done here

Example of modeladmin registration that we need to support:

```python
# models.py
class SalesforceImportLog(models.Model):

    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    ACTIONS = [(x, x) for x in [CREATE, UPDATE, DELETE]]

    timestamp = models.DateTimeField(auto_now_add=True, editable=False)
    action = models.CharField(max_length=255, choices=ACTIONS)
    model = models.CharField(max_length=255)
    contact = models.CharField(max_length=255)
    reference = models.CharField(max_length=255)
    success = models.BooleanField()
    information = models.JSONField()

    def time(self):
        return self.timestamp.strftime("%Y-%m-%d %H:%M UTC")

    time.admin_order_field = "timestamp"

    def __str__(self):
        return (
            f"""{self.time()}: """
            f"""{self.reference}: {self.action} {self.model}{'' if self.success else ': FAIL'}"""
        )
```

```python
# wagtail_hooks.py
class SalesforceImportLogAdmin(ModelAdmin):
    model = SalesforceImportLog

    class SalesforceImportLogPermissionHelper(PermissionHelper):
        def user_can_create(self, user):
            return False

        def user_can_edit_obj(self, user, obj):
            return False

        def user_can_delete_obj(self, user, obj):
            return False

    permission_helper_class = SalesforceImportLogPermissionHelper

    inspect_view_enabled = True

    menu_label = "Salesforce import log"
    menu_icon = "user"
    menu_order = 1000
    add_to_settings_menu = True
    exclude_from_explorer = True
    list_display = ("time", "reference", "action", "model", "success")
    list_filter = ("action", "model", "success")
    search_fields = ("reference",)
    ordering = ("-id",)


modeladmin_register(SalesforceImportLogAdmin)
```

Other test on other live sites reveal that if an app is not installed we the urls are generated when they shouldn't be.

Try setting up a most basic site without any optional apps and see if the urls are generated.