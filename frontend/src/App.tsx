import axios from 'axios';
import React from 'react';
import { DonutChart } from './components/pieChart';


const chartdata = [  {    name: "SolarCells",    amount: 4890,  },  {    name: "Glass",    amount: 2103,  },  {    name: "JunctionBox",    amount: 2050,  },  {    name: "Adhesive",    amount: 1300,  },  {    name: "BackSheet",    amount: 1100,  },  {    name: "Frame",    amount: 700,  },  {    name: "Encapsulant",    amount: 200,  },]

export function App() {
  const [, setMessage] = React.useState<string>('');

	React.useEffect(() => {
		axios.get('http://127.0.0.1:5000/')
		.then(response => setMessage(response.data))
		.catch(error => console.error('Error fetching data', error));
	}, []);
  
  return (
    <div>
      <DonutChart    className="mx-auto"    data={chartdata}    category="name"    value="amount"    showLabel={true}    valueFormatter={(number: number) =>      `$${Intl.NumberFormat("us").format(number).toString()}`    }  />
    </div>
  );
}
