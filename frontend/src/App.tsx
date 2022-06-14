import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { CartesianGrid, Legend, Scatter, ScatterChart, Tooltip, XAxis, YAxis, ZAxis } from 'recharts';
import './App.css';

function App() {
  const { register, handleSubmit, formState: { errors } } = useForm();
  const [data, setData] = useState([]);
  const onSubmit = (data: any) => {
    fetch("/optimize", {
      method: "post",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        "assets": data["Assets"].split(","),
        "start": data["Start"],
        "end": data["End"],
        "population_size": Number(data["Population size"]),
        "algorithm": data["Algorithm"],
        "n_gen_per_iter": Number(data["Generations per iteration"]),
        "n_iterations": Number(data["Number of iterations"])
      })
    })
    .then(res => res.json())
    .then(results => setData(results))
    .catch(() => alert("Something went wrong, check all the fiedls and try again"));
  }
  return (
    <div className="App">
      <div className="App-header">
        <div className="container form-container">
          <form onSubmit={handleSubmit(onSubmit)}>
              <input type="text" placeholder="Assets, separate with comma" {...register("Assets", {})} />
              <input type="text" placeholder="Start (2015/01/01)" {...register("Start", {})} />
              <input type="text" placeholder="End (2019/12/31)" {...register("End", {})} />
              <input type="number" placeholder="Population size" {...register("Population size", {})} />
              <input type="number" placeholder="Generations per iteration" {...register("Generations per iteration", {})} />
              <input type="number" placeholder="Number of iterations" {...register("Number of iterations", {})} />
              <label>Algorithm: </label>
              <select {...register("Algorithm")}>
                <option value="RVEA">RVEA</option>
                <option value="NSGAIII">NSGAIII</option>
              </select>
              <input type="submit" />
          </form>
        </div>
        <div className="container plot-container">
          <ScatterChart width={500} height={500}
            margin={{ top: 20, right: 20, bottom: 10, left: 10 }}>
            <XAxis type='number' label="Risk" dataKey="variance" name="variance" />
            <YAxis type='number' label="Returns" dataKey="returns" name="returns" />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Scatter data={data} fill="#82ca9d" />
          </ScatterChart>
        </div>

      </div>
    </div>
  );
}

const CustomTooltip = ({ active, payload } : any) => {
  if (active && payload && payload.length) {
    const x = payload[0].payload;
    const content = Object.keys(x).map((key) => {
      return <p>{`${key}: ${x[key] * 100}%`}</p>
    })
    return (
      <div className="custom-tooltip">
        {content}
      </div>
    );
  }

  return null;
};

export default App;
