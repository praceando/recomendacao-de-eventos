from flask import Flask
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import CountVectorizer
import psycopg2
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np

load_dotenv()
app = Flask(__name__)

def connect_db() -> psycopg2.extensions.connection:
    try:
        conn = psycopg2.connect(os.getenv("LINK_2ANO_POSTGRESQL"))
        if conn:
            return conn
        return None
    except Exception as e:
        print(e)
        
def select_query(query:str,user_id:int=0) -> pd.DataFrame:
    conn = connect_db()
    cursor = conn.cursor()
    
    if user_id>0:
        cursor.execute(query,(user_id,))
    else:
        cursor.execute(query)
    
    result = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    
    dataframe = pd.DataFrame(result, columns=columns)
    return dataframe

def search_vector(index:np.ndarray,dataframe:pd.DataFrame) -> list:
    eventos_id = []
    for i in index[0]:
        eventos_id.append(dataframe.loc[i,"id_evento"])
    return eventos_id
    
@app.route("/recomendation/<int:user_id>/", methods=["GET"])
def recomendation(user_id:int):
    
    df_tag_eventos = select_query("""SELECT e.id_evento, ARRAY_AGG(et.cd_tag) AS array_tag FROM evento e
                                     JOIN evento_tag et ON et.cd_evento = e.id_evento
                                     WHERE e.dt_desativacao IS NULL
                                     GROUP BY e.id_evento
                                     ORDER BY e.id_evento;""")

    df_tag_users = select_query("""SELECT ut.cd_consumidor, ARRAY_AGG(ut.cd_tag) AS array_tag FROM usuario_tag ut
                                   WHERE ut.cd_consumidor=%s
                                   GROUP BY ut.cd_consumidor;""",user_id)
    
    counts_tag_users = df_tag_users["array_tag"].value_counts().reset_index()
    tags_eventos = df_tag_eventos['array_tag'].apply(lambda x: ' '.join(map(str, x)))
        
    # Criação da matriz de vetores binários de tags usando CountVectorizer
    vectorizer = CountVectorizer()
    matrix_counter = vectorizer.fit_transform(tags_eventos).toarray()

    # # Convertendo o perfil do usuário para um vetor na mesma dimensão
    tags_counter = [int(i) for i in vectorizer.get_feature_names_out()]  # Obtenha a lista de todas as tags
    perfil_vetor =  np.array([counts_tag_users.loc[counts_tag_users['array_tag'] == tag, 'count'].values[0] if tag in counts_tag_users['array_tag'].values else 0 for tag in tags_counter])

    # Aplicação do Nearest Neighbors (kNN) para encontrar os eventos mais similares
    nbrs = NearestNeighbors(n_neighbors=3, metric="euclidean").fit(matrix_counter)
    _, index = nbrs.kneighbors([perfil_vetor])
    
    eventos_ids = search_vector(index, df_tag_eventos)
    # Garantir que os IDs sejam convertidos em um tipo serializável
    return {"eventos_ids": [int(evento_id) for evento_id in eventos_ids]}


if __name__ == "__main__":
    app.run(debug=False,port=5002,host='0.0.0.0')
