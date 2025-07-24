import React, { useEffect, useState } from 'react';
import './RSSFeed.css';

const RSSFeed = () => {
  const [articles, setArticles] = useState([]);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0); // État pour la page actuelle
  const [totalPages, setTotalPages] = useState(0); // État pour le nombre total de pages
  const [isLoading, setIsLoading] = useState(true);
  useEffect(() => {
    setIsLoading(true);
    fetch(`http://localhost:8080/api/news?page=${page}&size=12`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Erreur HTTP: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        console.log('Données reçues de l\'API :', data);
        setArticles(data.content);
        setTotalPages(data.totalPages);
        setIsLoading(false);
      })
      .catch((error) => {
        console.error('Erreur lors de la récupération des données:', error);
        setError('Erreur lors du chargement des articles');
        setIsLoading(false);
      });
  }, [page]);
  
  if (isLoading) {
    return <div>Chargement des articles...</div>;
  }

  const handlePreviousPage = () => {
    if (page > 0) {
      setPage(page - 1);
    }
  };

  const handleNextPage = () => {
    if (page < totalPages - 1) {
      setPage(page + 1);
    }
  };

  if (error) {
    return <div>{error}</div>;
  }

  if (articles.length === 0) {
    return <div>Chargement des articles...</div>;
  }

  return (
    <div className="rss-feed">
      <h1>Flux RSS</h1>
      <div className="rss-articles-grid">
        {articles.map((article) => (
          <div key={article.id} className="rss-article">
            {/* Titre de l'article */}
            <div className="article-title">
              <h2>
                <a href={article.link} target="_blank" rel="noopener noreferrer">
                  {article.title}
                </a>
              </h2>
            </div>
            {/* Image de l'article */}
            {article.imageUrl && (
              <div className="article-image">
                <img src={article.imageUrl} alt={article.title} className="rss-image" />
              </div>
            )}
            {/* Contenu de l'article */}
            <div className="article-content">
              <p>{article.summary}</p>
              <p>Publié le {new Date(article.published).toLocaleDateString()}</p>
            </div>
          </div>
        ))}
      </div>
      {/* Pagination */}
      <div className="pagination">
        <button onClick={handlePreviousPage} disabled={page === 0}>
          Précédent
        </button>
        <span>
          Page {page + 1} sur {totalPages}
        </span>
        <button onClick={handleNextPage} disabled={page >= totalPages - 1}>
          Suivant
        </button>
      </div>
    </div>
  );
};

export default RSSFeed;
