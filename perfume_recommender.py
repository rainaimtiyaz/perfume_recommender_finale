from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import jaccard_score
import pandas as pd
import numpy as np
import re
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

class PerfumeRecommender:
    def __init__(self, data_path):
        self.df = pd.read_csv(data_path)
        self.df['Rating'] = pd.to_numeric(self.df['Rating'], errors='coerce')
        self.df = self.df.dropna(subset=['Combined_Features', 'Rating'])
        self.vectorizer = TfidfVectorizer(tokenizer=lambda x: x.split(' '))
        self.tfidf_matrix = self.vectorizer.fit_transform(self.df['Combined_Features'])
        self.binary_matrix = (self.tfidf_matrix > 0).astype(int)
        
        self.stopword_factory = StopWordRemoverFactory()
        self.stopwords = self.stopword_factory.get_stop_words()
        self.stopwords.extend(['parfum', 'perfume', 'parfume', 'notes', 'aroma', 'wangi'])
    
    def get_recommendations(self, gender, time_usage, description, exclusions, top_n=3):
        print("\n=== DEBUGGING ===")
        print(f"Original Input: gender={gender}, time={time_usage}, desc={description}, excl={exclusions}")
        
        description = description.lower()
        exclusions = exclusions.lower() if exclusions else ""

        desc_keywords, rating_filter = self._extract_keywords_and_rating(description)
        excl_keywords = self._extract_keywords(exclusions)
        
        print(f"Desc Keywords: {desc_keywords}")
        print(f"Rating Filter: {rating_filter}")
        print(f"Excl Keywords: {excl_keywords}")

        filtered_df = self.df[
            (self.df['Gender'].str.lower() == gender.lower()) & 
            (self.df['Time Usage'].str.lower() == time_usage.lower())
        ].copy()
        print(f"\nInitial filter count: {len(filtered_df)}")

        for i, keyword in enumerate(desc_keywords):
            if keyword == 'lokal':
                filtered_df = filtered_df[filtered_df['Negara'].str.lower().str.contains('indonesia', na=False)]
                print(f"After lokal filter ({i+1}/{len(desc_keywords)}): {len(filtered_df)} rows")
            else:
                filtered_df = filtered_df[
                    filtered_df['Combined_Features'].str.lower().str.contains(
                        rf'\b{re.escape(keyword)}\b', regex=True, na=False
                    )
                ]
                print(f"After '{keyword}' filter ({i+1}/{len(desc_keywords)}): {len(filtered_df)} rows")
            
            if filtered_df.empty:
                print("! Filter resulted in empty dataframe !")
                return None

        if rating_filter:
            if rating_filter['type'] == 'above':
                filtered_df = filtered_df[filtered_df['Rating'] > rating_filter['value']]
                print(f"After rating > {rating_filter['value']} filter: {len(filtered_df)} rows")
            elif rating_filter['type'] == 'below':
                filtered_df = filtered_df[filtered_df['Rating'] < rating_filter['value']]
                print(f"After rating < {rating_filter['value']} filter: {len(filtered_df)} rows")
            
            if filtered_df.empty:
                print("! Rating filter resulted in empty dataframe !")
                return None

        for i, keyword in enumerate(excl_keywords):
            filtered_df = filtered_df[
                ~filtered_df['Combined_Features'].str.lower().str.contains(
                    rf'\b{re.escape(keyword)}\b', regex=True, na=False
                )
            ]
            print(f"After excluding '{keyword}' ({i+1}/{len(excl_keywords)}): {len(filtered_df)} rows")
            
            if filtered_df.empty:
                print("! Exclusion resulted in empty dataframe !")
                return None

        if desc_keywords:
            query_vec = self.vectorizer.transform([' '.join(desc_keywords)])
            query_binary = (query_vec > 0).astype(int).toarray()[0]
            
            similarities = []
            for idx in filtered_df.index:
                item_binary = self.binary_matrix[idx].toarray()[0]
                sim = jaccard_score(query_binary, item_binary, average='binary')
                similarities.append(sim)
            
            filtered_df['similarity'] = similarities
            filtered_df = filtered_df.sort_values('similarity', ascending=False)
        else:
            filtered_df['similarity'] = 0
            filtered_df = filtered_df.sort_values('Rating', ascending=False)
        
        print("\nFinal candidates:")
        print(filtered_df[['Brand', 'Perfume Name', 'Rating', 'Negara', 'similarity']].head())
        
        return filtered_df.head(top_n) if not filtered_df.empty else None
    
    def _extract_keywords_and_rating(self, text):
        keywords = []
        rating_filter = None

        rating_above = re.search(r'rating\w*\s*(?:di\s*)?(?:atas|lebih\s*dari|>)\s*([\d.]+)', text)
        rating_below = re.search(r'rating\w*\s*(?:di\s*)?(?:bawah|kurang\s*dari|<)\s*([\d.]+)', text)
        
        if rating_above:
            rating_filter = {'type': 'above', 'value': float(rating_above.group(1))}
            text = text.replace(rating_above.group(0), '')
        elif rating_below:
            rating_filter = {'type': 'below', 'value': float(rating_below.group(1))}
            text = text.replace(rating_below.group(0), '')

        if 'lokal' in text or 'local' in text:
            keywords.append('lokal')
            text = re.sub(r'(lokal|local)', '', text)

        tokens = re.findall(r'\b[a-z]+\b', text.lower())
        keywords.extend([
            token for token in tokens 
            if token in self.vectorizer.get_feature_names_out() 
            and token not in self.stopwords
        ])
        
        return keywords, rating_filter
    
    def _extract_keywords(self, text):
        if not text:
            return []

        tokens = re.findall(r'\b[a-z]+\b', text.lower())
        return [
            token for token in tokens 
            if token in self.vectorizer.get_feature_names_out() 
            and token not in self.stopwords
        ]

def preprocess_text(text):
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text