from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from .forms import LoginForm, UserRegistrationForm, TextInput
from django.contrib.auth.decorators import login_required
#new feature:
from textsummary_app.randomscript import example

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # create a new user object but not saving yet
            new_user = user_form.save(commit=False)
            #set password
            new_user.set_password(
                user_form.cleaned_data['password'])
            #save user object
            new_user.save()
            return render(request, 'textsummary_app/register_done.html',{'new_user':new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'textsummary_app/register.html',{'user_form':user_form})


def user_login(request):
    if request.method == 'POST': #check whether method is POST or GET
        form = LoginForm(request.POST)
        if form.is_valid(): #check whether form is valid (e.g. form is filled in where required)
            cd = form.cleaned_data #submitted data passed to the server as string, here Django converts data to the right type
            user = authenticate(request,
                                username=cd['username'],
                                password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated '\
                                        'successfully')
                else:
                    return HttpResponse('Disabled account') #if the user is not active
            else:
                return HttpResponse('Invalid login') #if the user is not authenticated
    else:
        form = LoginForm()
    return render(request, 'textsummary_app/login.html', {'form':form})

@login_required
# checks whether the current user is authenticated. If yes, it executes the view, if not, redirects to the login URL
def textinput(request):
    return render(request, 'textsummary_app/textinput.html',{'section': 'textinput'})

def script(request):
    text = request.POST.get('handle', None)
    #new feature:
    import nltk
    from nltk.corpus import stopwords
    from nltk.cluster.util import cosine_distance
    import numpy as np
    import networkx as nx

    def read_article(text, top_n):
        filedata = text.splitlines()
        sentences = []

        for i in range(top_n):
            article = filedata[i].split(". ")
            for sentence in article:
                sentences.append(sentence.replace("[^a-zA-Z]", " ").split(" "))
                #sentences.pop()

        return sentences

    def sentence_similarity(sent1, sent2, stopwords=None):
        if stopwords is None:
            stopwords = []

        sent1 = [w.lower() for w in sent1]
        sent2 = [w.lower() for w in sent2]

        all_words = list(set(sent1 + sent2))

        vector1 = [0] * len(all_words)
        vector2 = [0] * len(all_words)

        # build the vector for the first sentence
        for w in sent1:
            if w in stopwords:
                continue
            vector1[all_words.index(w)] += 1

        # build the vector for the second sentence
        for w in sent2:
            if w in stopwords:
                continue
            vector2[all_words.index(w)] += 1

        return 1 - cosine_distance(vector1, vector2)

    def build_similarity_matrix(sentences, stop_words):
        # Create an empty similarity matrix
        similarity_matrix = np.zeros((len(sentences), len(sentences)))

        for idx1 in range(len(sentences)):
            for idx2 in range(len(sentences)):
                if idx1 == idx2: #ignore if both are same sentences
                    continue
                similarity_matrix[idx1][idx2] = sentence_similarity(sentences[idx1], sentences[idx2], stop_words)

        return similarity_matrix


    def generate_summary(text, top_n=5):
        nltk.download("stopwords")
        stop_words = stopwords.words('english')
        summarize_text = []

        # Step 1 - Read text anc split it
        sentences =  read_article(text, top_n)

        # Step 2 - Generate Similary Martix across sentences
        sentence_similarity_martix = build_similarity_matrix(sentences, stop_words)

        # Step 3 - Rank sentences in similarity martix
        sentence_similarity_graph = nx.from_numpy_array(sentence_similarity_martix)
        scores = nx.pagerank(sentence_similarity_graph)

        # Step 4 - Sort the rank and pick top sentences
        ranked_sentence = sorted(((scores[i],s) for i,s in enumerate(sentences)), reverse=True)
        # print("Indexes of top ranked_sentence order are ", ranked_sentence)

        for i in range(top_n):
          summarize_text.append(" ".join(ranked_sentence[i][1]))

        # Step 5 - Offcourse, output the summarize text
        # print("Summarize Text: \n", " ".join(summarize_text))
        a = "Summarize Text: \n"
        b = " ".join(summarize_text)

        return a + b

    result = generate_summary(text, 10)
    #end of new feature
    return render(request, 'textsummary_app/result.html', {'result': result})
