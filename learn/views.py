from django.shortcuts import render
from django.http import JsonResponse, HttpResponseNotAllowed
from .models import Question, Answer, Category
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import re

# Caminho para o msedgedriver.exe na pasta learn
driver_path = os.path.join(os.path.dirname(__file__), 'msedgedriver.exe')
service = EdgeService(executable_path=driver_path)
options = webdriver.EdgeOptions()
options.add_argument("user-data-dir=C:/Users/SEU_USUARIO/AppData/Local/Microsoft/Edge/User Data/Selenium")  # Ajuste o caminho do perfil
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--disable-blink-features=AutomationControlled")

# Inicializar o navegador globalmente
browser = None

def initialize_browser():
    global browser
    if browser is None:
        browser = webdriver.Edge(service=service, options=options)
        browser.get('https://chatgpt.com/?default=c&default=&temporary-chat=true')
        WebDriverWait(browser, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea'))
        )

predefined_text = """
Você é um professor muito habilidoso, você tem amplo conhecimento de todas as materias do mundo, pode acessar a internet para pesquisar tambem, e deve ter uma didatica perfeita. Por favor, responda à pergunta com a categoria (matéria escolar) no começo do texto, na categoria nao pode conter :, ;, ', ", {, }, [, ], !, `, ~, <, >, /, ?  e nem numeros.. As categorias devem ser matérias escolares como Matemática, Física, Química, História, Geografia, Biologia, etc.
"""

def home(request):
    initialize_browser()
    categories = Category.objects.all()
    return render(request, 'index.html', {'categories': categories})

def ask_question(request):
    if request.method == 'POST':
        question_text = request.POST.get('question')
        full_text = f"{predefined_text}\n\n{question_text}"

        try:
            initialize_browser()

            input_box = browser.find_element(By.CSS_SELECTOR, 'textarea')
            input_box.clear()
            input_box.send_keys(full_text)
            input_box.send_keys(Keys.RETURN)

            # Espera até que a resposta esteja presente
            WebDriverWait(browser, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class*="result-streaming"]'))
            )
            WebDriverWait(browser, 120).until_not(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class*="result-streaming"]'))
            )

            response_elements = browser.find_elements(By.CSS_SELECTOR, 'div.markdown.prose.w-full.break-words.dark\\:prose-invert.dark')
            if response_elements:
                answer_html = response_elements[-1].get_attribute('outerHTML')
                
                # Extração da categoria da resposta (primeira ocorrência de <strong>)
                category_match = re.search(r'<strong>(.*?)</strong>', answer_html)
                if category_match:
                    category_name = category_match.group(1)
                    category, _ = Category.objects.get_or_create(name=category_name)
                else:
                    category = None
            else:
                answer_html = "Não foi possível obter a resposta do ChatGPT."
                category = None
        except Exception as e:
            answer_html = f"Erro ao obter resposta do ChatGPT: {e}"
            category = None

        question = Question.objects.create(text=question_text, category=category)
        Answer.objects.create(question=question, text=answer_html)

        return JsonResponse({'question': question_text, 'answer': answer_html})
    else:
        return HttpResponseNotAllowed(['POST'])

def get_questions(request):
    categories = Category.objects.all().prefetch_related('questions__answers')
    data = []
    for category in categories:
        category_data = {
            'name': category.name,
            'questions': []
        }
        for question in category.questions.all():
            question_data = {
                'question': question.text,
                'answers': [answer.text for answer in question.answers.all()]
            }
            category_data['questions'].append(question_data)
        data.append(category_data)
    return JsonResponse(data, safe=False)

def get_questions_by_category(request, category_id):
    category = Category.objects.get(id=category_id)
    questions = category.questions.all().prefetch_related('answers')
    data = {
        'name': category.name,
        'questions': [{'question': q.text, 'answers': [a.text for a in q.answers.all()]} for q in questions]
    }
    return JsonResponse(data, safe=False)

def search_questions(request):
    query = request.GET.get('q', '')
    results = []
    if query:
        answers = Answer.objects.filter(text__icontains=query).select_related('question__category')
        for answer in answers:
            results.append({
                'question': answer.question.text,
                'category': answer.question.category.name,
                'answer': answer.text
            })
    return JsonResponse(results, safe=False)
