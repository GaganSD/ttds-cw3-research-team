import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import ResultsPage  from './components/resultsPage';
import reportWebVitals from './reportWebVitals';
import { BrowserRouter, Route, Routes } from 'react-router-dom';


ReactDOM.render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route exact path="/" element={<App/>}/>
        <Route exact path="/search/:query/:df/:dt/:alg/:srchtyp/:ds/:pn" element={<ResultsPage/>}/>
      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
  document.getElementById('root')
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
