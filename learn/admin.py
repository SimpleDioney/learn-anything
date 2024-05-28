from django.contrib import admin
from .models import Question, Answer, Category

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'category', 'created_at')
    inlines = [AnswerInline]

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)
admin.site.register(Category, CategoryAdmin)
