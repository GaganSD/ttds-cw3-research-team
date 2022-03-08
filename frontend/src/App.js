import logo from './logo.svg';
import './App.css';
import * as React from 'react';
import Button from '@mui/material/Button';
import ButtonGroup from '@mui/material/ButtonGroup';
import SearchButton from './components/serachbutton';
import SearchField from './components/search';
import { styled } from '@mui/material/styles';
import Typography from '@mui/material/Typography';
import Options from './components/options'
import JsonResults from './example.json'


function App() {

  const [search, setSearch] = React.useState('');
 

  function Search() {
    return fetch('http://127.0.0.1:5000/' + search).then(response => response.json()).then(data => console.log(data));
  }

  function TextEntered(searchval){
      setSearch(searchval);
  }


  return (
    <div className="App">
      <div className="Logo">
        <Typography variant='h1' gutterbottom>
          ReSearchEd
        </Typography>
      </div>
      <div className='SearchOptions'>
        <SearchField parentCallback = {TextEntered}/>
        <div className='Options'>
          <Options/>
        </div>
      </div>
      <SearchButton parentCallback = {Search}/>
      <div>
      {JsonResults.Results.map((name, key) => {
        return <p key={key}>
          <h1>{name.title}</h1>
          <p>{name.date}</p>
          <a>{name.url}</a>
          <p>{name.description}</p>
          </p>;
      })}
      </div>
    </div>
  )

}


export default App;