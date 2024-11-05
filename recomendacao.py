from flask import Flask, jsonify
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
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def select_query(query:str, user_id:int = 0) -> pd.DataFrame:
    conn = connect_db()
    if conn is None:
        return pd.DataFrame()  # Retorna DataFrame vazio em caso de falha na conexão
    with conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (user_id,))
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return pd.DataFrame(result, columns=columns)

def search_vector(index: np.ndarray, dataframe: pd.DataFrame) -> list:
    return dataframe.loc[index[0], "id_evento"].tolist()

@app.route("/recomendation/<int:user_id>/", methods=["GET"])
def recomendation(user_id: int):
    # Consultas combinadas
    query = """
        SELECT 
            e.id_evento, 
            ARRAY_AGG(et.cd_tag) AS array_tag, 
            ARRAY_AGG(ut.cd_tag) AS user_tags 
        FROM 
            evento e
        JOIN 
            evento_tag et ON et.cd_evento = e.id_evento
        LEFT JOIN 
            usuario_tag ut ON ut.cd_consumidor = %s
        WHERE 
            e.dt_desativacao IS NULL
        GROUP BY 
            e.id_evento;
    """
    df_eventos = select_query(query, (user_id,))

    if df_eventos.empty:
        return jsonify({"eventos_ids": []})

    # Processamento das tags
    df_eventos['array_tag'] = df_eventos['array_tag'].apply(lambda x: ' '.join(map(str, x)))
    user_tags = df_eventos['user_tags'].values[0] if df_eventos['user_tags'].size > 0 else []

    # Contagem das tags do usuário
    counts_tag_users = pd.Series(user_tags).value_counts().reset_index(name='count')
    counts_tag_users.columns = ['tag', 'count']

    # Matriz de características
    vectorizer = CountVectorizer()
    matrix_counter = vectorizer.fit_transform(df_eventos['array_tag']).toarray()

    # Vetor de perfil do usuário
    perfil_vetor = np.array([counts_tag_users[counts_tag_users['tag'] == tag]['count'].values[0] if tag in counts_tag_users['tag'].values else 0 for tag in vectorizer.get_feature_names_out()])

    # k-NN
    nbrs = NearestNeighbors(n_neighbors=8, metric="euclidean").fit(matrix_counter)
    _, index = nbrs.kneighbors([perfil_vetor])

    eventos_ids = search_vector(index, df_eventos)
    print(eventos_ids)

    return jsonify({"eventos_ids": [int(evento_id) for evento_id in eventos_ids]})

if __name__ == "__main__":
    app.run(debug=False, port=5002, host='0.0.0.0')
