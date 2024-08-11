from flask import Flask, jsonify
import math
from flask import Flask, render_template, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField


def load_vocab():
    vocab = {}
    with open('tf-idf/vocab.txt', 'r') as f:
        vocab_terms = f.readlines()
    with open('tf-idf/idf-values.txt', 'r') as f:
        idf_values = f.readlines()
    
    for (term,idf_value) in zip(vocab_terms, idf_values):
        vocab[term.strip()] = int(idf_value.strip())
    
    return vocab

def load_documents():
    documents = []
    with open('tf-idf/documents.txt', 'r') as f:
        documents = f.readlines()
    return documents

def load_inverted_index():
    inverted_index = {}
    with open('tf-idf/inverted-index.txt', 'r') as f:
        inverted_index_terms = f.readlines()

    for row_num in range(0,len(inverted_index_terms),2):
        term = inverted_index_terms[row_num].strip()
        documents = inverted_index_terms[row_num+1].strip().split()
        inverted_index[term] = documents
    
    return inverted_index



vocab_idf_values = load_vocab()
documents = load_documents()
inverted_index = load_inverted_index()


def get_tf_dictionary(term):
    tf_values = {}
    if term in inverted_index:
        for document in inverted_index[term]:
            if document not in tf_values:
                tf_values[document] = 1
            else:
                tf_values[document] += 1
                
    for document in tf_values:
        tf_values[document] /= len(documents[int(document)])
    
    return tf_values

def get_idf_value(term):
    return math.log(len(documents)/vocab_idf_values[term])

def calculate_sorted_order_of_documents(query_terms):
    ans=[]
    potential_documents = {}
    for term in query_terms:
        if vocab_idf_values.get(term,0) == 0:
            continue
        tf_values_by_document = get_tf_dictionary(term)
        idf_value = get_idf_value(term)
        
        for document in tf_values_by_document:
            if document not in potential_documents:
                potential_documents[document] = tf_values_by_document[document] * idf_value
            potential_documents[document] += tf_values_by_document[document] * idf_value
    
    # divite by the length of the query terms
    for document in potential_documents:
        potential_documents[document] /= len(query_terms)

    potential_documents = dict(sorted(potential_documents.items(), key=lambda item: item[1], reverse=True))
    ##print(potential_documents)
    if (len(potential_documents) == 0):
            print("No matching question found. Please search with more relevant terms.")
    for document_index in potential_documents:
        p=int(document_index)
        filename = 'Leetcode-Questions-Scrapper/Qdata/'+str(p)+'/'+str(p)+'.txt'
        with open("Leetcode-Questions-Scrapper/index.txt", "r",encoding="iso-8859-1") as g:
            t=g.readlines()
        with open("Leetcode-Questions-Scrapper/Qindex.txt", "r") as f:
            k=f.readlines()
            ##print(f"Problem link : {k[p-1]} Score: {potential_documents[document_index]}")
            temp={"Question Link": k[p - 1][:-2], "Title": t[p-1]}
            if temp not in ans:
                ans.append(temp)
    return ans
##gg="allone".strip().split()
##print(len(calculate_sorted_order_of_documents(gg)))
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
class SearchForm(FlaskForm):
    search = StringField('Enter your search term')
    submit = SubmitField('Search')



@app.route("/", methods=['GET', 'POST'])
def home():
    form = SearchForm()
    results = []
    if form.validate_on_submit():
        query = form.search.data
        q_terms = [term.lower() for term in query.strip().split()]
        results = calculate_sorted_order_of_documents(q_terms)[:20:]
    return render_template('index.html', form=form, results=results)
