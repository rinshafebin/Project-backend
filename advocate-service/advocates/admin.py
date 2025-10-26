from django.contrib import admin
from advocates.models import Case, CaseDocument, CaseNote

@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'case_number', 'client', 'advocate', 'status', 'hearing_date', 'created_at')
    search_fields = ('title', 'case_number', 'client__username', 'advocate__username')
    list_filter = ('status', 'hearing_date', 'created_at')
    ordering = ('-created_at',)



@admin.register(CaseDocument)
class CaseDocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'case', 'document', 'uploaded_at', 'visible_to_client', 'visible_to_advocate')
    search_fields = ('case__title',)
    list_filter = ('visible_to_client', 'visible_to_advocate', 'uploaded_at')
    ordering = ('-uploaded_at',)


@admin.register(CaseNote)
class CaseNoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'case', 'created_by', 'created_at')
    search_fields = ('case__title', 'created_by__username')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
