const GoogleTrends = ({ trends }) => (
    <div className="google-trends">
      <h2>Google Trends</h2>
      <ul>
        {trends.map((trend, index) => (
          <li key={index}>{trend.name}: {trend.popularity}</li>
        ))}
      </ul>
    </div>
  );
    export default GoogleTrends;