from django.contrib import admin

@admin.action(description="이 항목만 활성화(동일 타입의 다른 항목 비활성)")
def activate_only(modeladmin, request, queryset):
    obj = queryset.first()
    if not obj:
        return
    obj.activate = True
    obj.save()

class BaseModalAdmin(admin.ModelAdmin):
    list_display = ("modal_title", "activate", "updated_at")
    list_filter = ("activate",)
    search_fields = ("modal_title",)
    actions = [activate_only]

class ImageOnlyAdmin(BaseModalAdmin): pass
class SingleBGAdmin(BaseModalAdmin): pass
class LinkVideoAdmin(BaseModalAdmin): pass
class RotateBGAdmin(BaseModalAdmin): pass