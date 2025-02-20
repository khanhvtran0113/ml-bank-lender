import axios from 'axios';
import React from 'react';

export function App() {
  const [message, setMessage] = React.useState<string>('');

	React.useEffect(() => {
		axios.get('http://127.0.0.1:5000/')
		.then(response => setMessage(response.data))
		.catch(error => console.error('Error fetching data', error));
	}, []);
  
  return (
    <div>
      {message}
    </div>
  );
}
