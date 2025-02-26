import axios from 'axios';
import React from 'react';
import FileUpload from './components/upload';


export function App() {
  const [, setMessage] = React.useState<string>('');

	React.useEffect(() => {
		axios.get('http://127.0.0.1:5000/')
		.then(response => setMessage(response.data))
		.catch(error => console.error('Error fetching data', error));
	}, []);
  
  return (
    <div>
      <FileUpload />
    </div>
  );
}
