import os
import re
from datetime import datetime

from django.shortcuts import render, redirect
from django.conf import settings
from django.template.defaultfilters import length
from django.template.response import TemplateResponse


def index(request):
    return TemplateResponse(request, 'index.html')

def contact(request):
    return TemplateResponse(request,"contact.html")

def articles(request):
    criteria = request.GET.get('sort')
    articles_dir = os.path.join(settings.BASE_DIR, 'AllArticles')
    articless = []
    for filename in os.listdir(articles_dir):
        file_path = os.path.join(articles_dir, filename)
        with (open(file_path, 'r', encoding='utf-8') as file):
            content = file.readlines()
            title = content[0]
            author = content[1]
            date = content[2]
            resource = content[3]
            articless.append({'date': date, 'resource': resource, 'author':author, 'title': title, 'content': ' '.join(content[4:len(content)]), 'filename': filename})
    if criteria:
        if criteria == 'author':
            articless = sorted(articless, key=lambda x: x['author'])
        elif criteria == 'date_back':
            articless = sorted(articless, key=lambda x: datetime.strptime(x['date'].strip().replace("Дата создания: ", ""),'%d.%m.%Y'))
        elif criteria == 'date':
            articless = sorted(articless, key=lambda x: datetime.strptime(x['date'].strip().replace("Дата создания: ", ""),'%d.%m.%Y'), reverse=True)
        elif criteria == 'resource':
            articless = sorted(articless, key=lambda x: x['resource'])
        elif criteria == 'title':
            articless = sorted(articless, key=lambda x: x['title'])

    author_filter = request.GET.get('author', '').strip().lower()
    date_filter = request.GET.get('date', '').strip()
    resource_filter = request.GET.get('resource', '').strip().lower()
    content_filter = request.GET.get('content', '').strip().lower()
    title_filter = request.GET.get('title', '').strip().lower()

    if title_filter:
        articless = [article for article in articless if title_filter in article['title'].lower()]
    if author_filter:
        articless = [article for article in articless if author_filter in article['author'].replace("Автор:  ", "").lower().strip()]
    if date_filter:
        filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date().strftime('%d.%m.%Y')
        articless = [article for article in articless if article['date'].replace("Дата создания: ", "").strip() == filter_date]
    if resource_filter:
        articless = [article for article in articless if resource_filter in article['resource'].replace("Ресурс:  ", "").strip().lower()]
    if content_filter:
        articless = [article for article in articless if content_filter in article['content'].strip().lower()]

    return render(request, 'articles.html', {'articles': articless})

def one_article(request, filename):
    articles_dir = os.path.join(settings.BASE_DIR, 'AllArticles')
    file_path = os.path.join(articles_dir, filename)
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.readlines()
        title = content[0]
    return render(request, 'one_article.html', {'title': title, 'content': ' '.join(content[4:length(content)])})


def create_article(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        author = "Автор: " + request.POST.get('author')
        date = "Дата создания: " + datetime.now().strftime('%d.%m.%Y')
        resource = "Ресурс: " + request.POST.get('resource')
        content = f"{title}\n{author}\n{date}\n{resource}\n\n{request.POST.get('content')}"
        articles_dir = os.path.join(settings.BASE_DIR, 'AllArticles')
        i =  length(os.listdir(articles_dir)) + 1
        res_i = 0
        for filename in os.listdir(articles_dir):
            i-=1
            match = int(re.findall(r'\d+', filename)[0])
            if match != i:
                res_i += i
                break
        if res_i == 0:
            res_i = length(os.listdir(articles_dir)) + 1
        if title and content and date and author and resource:
            filename = f"article-{res_i}.txt"
            file_path = os.path.join(settings.BASE_DIR, 'AllArticles', filename)
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            return redirect('articles')
    return render(request, 'create_article.html')

def delete_article(request):
    articles_dir = os.path.join(settings.BASE_DIR, 'AllArticles')

    if request.method == 'POST':
        articles_to_delete = request.POST.getlist('articles_to_delete')
        articles_titles = []
        if articles_to_delete:
            for ar in articles_to_delete:
                articles_titles.append(ar.strip())
            for filename in os.listdir(articles_dir):
                file_path = os.path.join(articles_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    title = file.readline().strip()
                    if title in articles_titles:
                        os.remove(file_path)

        return redirect('delete_article')
    articles_titles = []
    for filename in os.listdir(articles_dir):
        file_path = os.path.join(articles_dir, filename)
        with (open(file_path, 'r', encoding='utf-8') as file):
            content = file.readlines()
            title = content[0]
            articles_titles.append({'title':title})

    return render(request, 'delete_article.html',{'articles': articles_titles})


def edit_article(request, filename):
    file_path = os.path.join(settings.BASE_DIR, 'AllArticles', filename)


    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.readlines()
        article = {
            'filename': filename,
            'title': content[0].strip(),
            'author': content[1].strip(),
            'date': content[2].strip(),
            'resource': content[3].strip(),
            'content': '\n'.join(line.strip() for line in content[4:]),
        }

    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        resource = request.POST.get('resource')
        content = request.POST.get('content')
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(f"{title}\nАвтор: {author}\nДата создания: {datetime.now().strftime('%d.%m.%Y')}\nРесурс: {resource}\n\n{content}")
        return redirect('articles')

    # Отображение формы редактирования
    return render(request, 'edit_article.html', {'article': article})