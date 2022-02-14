import React from 'react';
import './App.css';
//import SearchBar from './SearchBar/SearchBar';

function App() {
  return (
    <div className="App">
      
      <h1 style={{ fontSize: "3rem" }}>Paper Dataset project!</h1>
      <input 
        id='query'
        style={{ fontSize: "3rem" }} 
        placeholder="Enter query here..."
      />
      <button 
      type="button" 
      style={{ fontSize: "3rem" }} 
      className="btn">Search!</button>
    </div>
   /* <div className="wrapper">
      <SearchBar title="Search" type="input">
        <div>search for something...</div>
      </SearchBar>
    </div> */
  );
  
}

export default App;
